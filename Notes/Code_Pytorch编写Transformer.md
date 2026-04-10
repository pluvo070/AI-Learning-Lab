预备工作


```python
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import math, copy, time
from torch.autograd import Variable
import matplotlib.pyplot as plt
import seaborn
seaborn.set_context(context="talk")
%matplotlib inline
```



# 模型架构

大部分序列到序列（seq2seq）模型都使用编码器-解码器结构。

编码器把一个输入序列$(x_{1},...x_{n})$映射到一个连续的表示$z=(z_{1},...z_{n})$中。

解码器对z中的每个元素，生成输出序列$(y_{1},...y_{m})$。解码器一个时间步生成一个输出。在每一步中，模型都是自回归的，在生成下一个结果时，会将先前生成的结果加入输入序列来一起预测。

先构建一个EncoderDecoder类来搭建一个seq2seq架构：


```python
class EncoderDecoder(nn.Module):
    def __init__(self, encoder, decoder, src_embed, tgt_embed, generator):
        super(EncoderDecoder, self).__init__()
        self.encoder = encoder
        self.decoder = decoder
        self.src_embed = src_embed # 源语言嵌入,输入的文字到向量
        self.tgt_embed = tgt_embed # 目标语言嵌入,已经输出的文字到向量
        self.generator = generator # 线性层加Softmax,将解码器输出映射到词概率
    # 向前传播： 先调用encode, 再调用decode
    def forward(self, src, tgt, src_mask, tgt_mask):
        return self.decode(self.encode(src, src_mask), src_mask,
                            tgt, tgt_mask)
    # 编码: 原文向量 src + 源语言掩码 → 生成矩阵 memory
    def encode(self, src, src_mask):
        return self.encoder(self.src_embed(src), src_mask)
    # 解码: 已生成文字的向量 + 编码器memory + 目标语言掩码 → 下一个词的向量
    def decode(self, memory, src_mask, tgt, tgt_mask):
        return self.decoder(self.tgt_embed(tgt), memory, src_mask, tgt_mask)
```

> `src_mask`：源语言掩码，在一个训练批次（Batch）里，每个句子的长度不一样。短句子后面会补上很多无意义的 `0`（即 `<pad>` 字符），告诉模型计算注意力（Attention）时请直接忽略它们
>
> `tgt_mask`：目标语言掩码，训练时我们会把整个目标句子一次性给模型。但实际预测时，模型必须根据前一个词预测下一个词，不能偷看。


```python
class Generator(nn.Module): # 定义生成器，由linear和softmax组成
    def __init__(self, d_model, vocab):
        super(Generator, self).__init__() # 执行父类的初始化程序
        self.proj = nn.Linear(d_model, vocab)
		# d_model是维度, vocab是单词表大小
    def forward(self, x):
        # softmax归一化
        return F.log_softmax(self.proj(x), dim=-1) 
    	# F是最前面定义的torch.nn.functional别名
```



## Encoder部分和Decoder部分

### Encoder

- **编码器整体**：由 N = 6 个完全相同的层组成


```python
def clones(module, N): # 克隆工厂
    return nn.ModuleList([copy.deepcopy(module) for _ in range(N)])
```


```python
class Encoder(nn.Module): # 完整的Encoder包含N层
    def __init__(self, layer, N):
        super(Encoder, self).__init__() # 执行父类 nn.Module 的初始化
        self.layers = clones(layer, N) # 克隆N层存入 self.layers
        self.norm = LayerNorm(layer.size) # 初始化一个层标准化组件
       
    def forward(self, x, mask): # 数据x依次穿过N个层
        for layer in self.layers:
            x = layer(x, mask) # 每一层接受上层输出并产生新输出，同时应用遮罩mask
        return self.norm(x) # 跑完所有层后，进行一次标准化
```

编码器的每层encoder包含Self Attention 子层和FFNN子层，每个子层都使用了残差连接，和层标准化（layer-normalization）。

- **每个子层的层标准化**


```python
class LayerNorm(nn.Module): # 层标准化
    def __init__(self, features, eps=1e-6):
        super(LayerNorm, self).__init__()
		# 定义学习参数 a_2（缩放倍数），初始全部设为 1
        self.a_2 = nn.Parameter(torch.ones(features))
        # 定义学习参数 b_2（偏移量），初始全部设为 0
        self.b_2 = nn.Parameter(torch.zeros(features))
        # eps 是一个微小的常数，防止数学计算中除以 0 导致报错
        self.eps = eps

    def forward(self, x):
		# 计算输入数据 x 在最后一个维度上的平均值（mean）
        mean = x.mean(-1, keepdim=True)
        # 计算输入数据 x 在最后一个维度上的标准差（std）
        std = x.std(-1, keepdim=True)
        # 核心公式：用数据减去均值再除以标准差，实现归一化
        # 最后乘上可学习的 a_2 并加上 b_2，让模型自己决定最舒服的数据分布
        return self.a_2 * (x - mean) / (std + self.eps) + self.b_2
```

> 我们称呼子层为：$\mathrm{Sublayer}(x)$，每个子层的最终输出是$\mathrm{LayerNorm}(x + \mathrm{Sublayer}(x))$。 dropout 被加在Sublayer上。
>
> 为了便于进行残差连接，模型中的所有子层以及embedding层产生的输出的维度都为 $d_{\text{model}}=512$。
>

- **子层包装连接器**：把任何一个子层（比如注意力机制或前馈网络）包起来，给它加上标准化、Dropout 和 残差连接。

  这个类用来处理单个Sublayer的输出，该输出将继续被输入下一个Sublayer：


```python
class SublayerConnection(nn.Module):
    def __init__(self, size, dropout):
        super(SublayerConnection, self).__init__()
        # 初始化层标准化组件
        self.norm = LayerNorm(size) 
        # 初始化 Dropout 层，用于随机丢弃一部分神经元防止过拟合
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, sublayer): # 将残差连接应用于任何相同尺寸的子层
        return x + self.dropout(sublayer(self.norm(x)))
        # 1. self.norm(x): 把输入进行标准化
        # 2. sublayer(...): 把标准化后的结果丢进子层（如注意力层）计算
        # 3. self.dropout(...): 对子层输出进行随机“剪枝”，防止模型死记硬背
        # 4. x + ...: 残差连接, 把原始输入 x 直接加到计算结果上
```

- **单个编码器层**：编码器层，由自注意力（self-attn）和前馈网络（feed forward）两个子层组成


```python
class EncoderLayer(nn.Module):
    def __init__(self, size, self_attn, feed_forward, dropout):
        super(EncoderLayer, self).__init__()
        self.self_attn = self_attn # 接收外部传进来的自注意力子层
        self.feed_forward = feed_forward # 接收外部传进来的前馈网络子层
        # 使用之前定义的 clones 工具，克隆 2 个“子层连接器”包装盒
        self.sublayer = clones(SublayerConnection(size, dropout), 2)
        self.size = size # 保存维度大小（如 512）

    def forward(self, x, mask): # 按照 Transformer 架构图进行连接
        # 1：处理自注意力子层
        # lambda x: ... 是一个匿名函数，把 self_attn 包装成只需一个参数的形式
        x = self.sublayer[0](x, lambda x: self.self_attn(x, x, x, mask))
        # 2：处理前馈网络子层，并返回最终结果
        return self.sublayer[1](x, self.feed_forward)
```

### Decoder

- **解码器整体**：也是由N = 6 个完全相同的decoder层组成。  


```python
class Decoder(nn.Module):
    def __init__(self, layer, N):
        super(Decoder, self).__init__()
        self.layers = clones(layer, N)
        self.norm = LayerNorm(layer.size)
        
    def forward(self, x, memory, src_mask, tgt_mask):
        for layer in self.layers:
            x = layer(x, memory, src_mask, tgt_mask)
        return self.norm(x)
```

-  **单个解码器**：由自注意力、源注意力（Encoder-Decoder Attn）和前馈网络组成

  > 单层decoder与单层encoder相比，decoder还有第三个子层，该层对encoder的输出执行attention：即encoder-decoder-attention层，q向量来自decoder上一层的输出，k和v向量是encoder最后层的输出向量。
  >
  > 与encoder类似，我们在每个子层再采用残差连接，然后进行层标准化。


```python
class DecoderLayer(nn.Module):
    def __init__(self, size, self_attn, src_attn, feed_forward, dropout):
        super(DecoderLayer, self).__init__()
        self.size = size
        self.self_attn = self_attn # 自己的自注意力（看已经翻译出的词）
        self.src_attn = src_attn   # 对源语言的注意力
        self.feed_forward = feed_forward # 前馈网络（加工信息）
        # 克隆 3 个连接器包装盒（比 Encoder 多一个）
        self.sublayer = clones(SublayerConnection(size, dropout), 3)
 
    def forward(self, x, memory, src_mask, tgt_mask):
        m = memory
        # 1：自注意力。处理已经生成的词，用 tgt_mask 防止看到未来的词
        x = self.sublayer[0](x, lambda x: self.self_attn(x, x, x, tgt_mask))
        # 2：源注意力
        # 第一个 x 是 Query（解码器出的题），两个 m 是 Key 和 Value（编码器的笔记）
        # 这一步让解码器在生成每个词时，都能去原文里找对应的重点
        x = self.sublayer[1](x, lambda x: self.src_attn(x, m, m, src_mask))
        # 3：前馈网络。最后做一次非线性变换并输出
        return self.sublayer[2](x, self.feed_forward)
```

- **遮罩函数**：对于单层decoder中的self-attention子层，我们需要使用mask机制，以防止在当前位置关注到后面的位置。


```python
def subsequent_mask(size): # 屏蔽掉后续位置的信息
    attn_shape = (1, size, size) # 定义遮罩的形状
    subsequent_mask = np.triu(np.ones(attn_shape), k=1).astype('uint8')
    # np.triu(...,k=1) 生成一个矩阵，右上角全是一，左下角全是零
    # .astype('uint8') 转换数据类型为 8 位无符号整型
    return torch.from_numpy(subsequent_mask) == 0
	# 我们需要的是：能看到的地方为 True (1)，不能看的地方为 False (0)
    # 所以让结果等于 0，就把上三角（未来信息）变成了 False    
```


## Attention

Attention功能可以描述为将query和一组key-value映射到输出，其中query、key、value和输出都是向量。输出为value的加权和，其中每个value的权重通过query与相应key的计算得到
我们将particular attention称之为“缩放的点积Attention”(Scaled Dot-Product Attention")。其输入为query、key(维度是$d_k$)以及values(维度是$d_v$)。我们计算query和所有key的点积，然后对每个除以 $\sqrt{d_k}$, 最后用softmax函数获得value的权重。                                                                                                                                                                                                                                                                                                                                                                                     


在实践中，我们同时计算一组query的attention函数，并将它们组合成一个矩阵$Q$。key和value也一起组成矩阵$K$和$V$。 我们计算的输出矩阵为：
                                                                 
$$
\mathrm{Attention}(Q, K, V) = \mathrm{softmax}(\frac{QK^T}{\sqrt{d_k}})V
$$

- **计算缩放点积注意力（Scaled Dot-Product Attention）**

  通过计算“问题”（Query）和“答案键”（Key）的匹配度，来决定应该从“内容”（Value）中提取多少信息。


```python
def attention(query, key, value, mask=None, dropout=None):
    # 1. 获取隐藏层维度 d_k（通常是 64），用于后续的缩放处理
    d_k = query.size(-1) 
    # 2. 计算匹配分数：将 Query 和 Key 的转置进行矩阵乘法, 并除以sqrt(d_k)进行缩放
    # 结果 scores 表示序列中每个词对其他词的“关联度”或“重要性”
    scores = torch.matmul(query, key.transpose(-2, -1)) \
             / math.sqrt(d_k)
    # 3. 如果有掩码，将掩码为0的位置替换为一个极小的负数,这样在经过后续Softmax时，这些位置的注意力会变成0，从而被“抹除”
    if mask is not None:
        scores = scores.masked_fill(mask == 0, -1e9)
	# 4. 对分数进行Softmax归一化，得到概率分布p_attn（所有权重加起来等于 1）
    p_attn = F.softmax(scores, dim = -1)
    # 5. 如果开启了Dropout，则随机丢弃一部分权重，增强模型的泛化能力
    if dropout is not None:
        p_attn = dropout(p_attn)
    # 6. 将权重 p_attn 乘以内容 Value，得到最终的加权结果, 同时返回权重矩阵p_attn方便以后可视化（看模型在关注哪里）
    return torch.matmul(p_attn, value), p_attn
```

> 两个最常用的attention函数是：加法attention 和 点积乘法attention
>
> 除了缩放因子$\frac{1}{\sqrt{d_k}}$ ，点积Attention跟我们的平时的点乘算法一样。加法attention使用具有单个隐层的前馈网络计算相似度。虽然理论上点积attention和加法attention复杂度相似，但在实践中，点积attention可以使用高度优化的矩阵乘法来实现，因此点积attention计算更快、更节省空间。
>
> 当$d_k$ 的值比较小的时候，这两个机制的性能相近。当$d_k$比较大时，加法attention比不带缩放的点积attention性能好。我们怀疑，对于很大的$d_k$值, 点积大幅度增长，将softmax函数推向具有极小梯度的区域。(为了说明为什么点积变大，假设q和k是独立的随机变量，均值为0，方差为1。那么它们的点积$q \cdot k = \sum_{i=1}^{d_k} q_ik_i$, 均值为0方差为$d_k$)。为了抵消这种影响，我们将点积缩小 $\frac{1}{\sqrt{d_k}}$倍。     
>
> Multi-head attention允许模型同时关注来自不同位置的不同表示子空间的信息，如果只有一个attention head，向量的表示能力会下降。
> $$
> \mathrm{MultiHead}(Q, K, V) = \mathrm{Concat}(\mathrm{head_1}, ..., \mathrm{head_h})W^O    \\                                           
>     \text{where}~\mathrm{head_i} = \mathrm{Attention}(QW^Q_i, KW^K_i, VW^V_i)
> $$
>
> 其中映射由权重矩阵完成：$W^Q_i \in \mathbb{R}^{d_{\text{model}} \times d_k}$, $W^K_i \in \mathbb{R}^{d_{\text{model}} \times d_k}$, $W^V_i \in \mathbb{R}^{d_{\text{model}} \times d_v}$ and $W^O \in \mathbb{R}^{hd_v \times d_{\text{model}}}$。 
>
>  在这项工作中，我们采用$h=8$个平行attention层或者叫head。对于这些head中的每一个，我们使用$d_k=d_v=d_{\text{model}}/h=64$。由于每个head的维度减小，总计算成本与具有全部维度的单个head attention相似。 

- **多头注意力类**：


```python
class MultiHeadedAttention(nn.Module):
    def __init__(self, h, d_model, dropout=0.1): # 头数 h, 模型总维度 d_model
        super(MultiHeadedAttention, self).__init__()
        assert d_model % h == 0 	# 确保总维度能被头数整除
        self.d_k = d_model // h  	# 每个小头分配到的维度 d_k = 64
        self.h = h
        # 定义 4 个线性层：3 个用于产生 Q、K、V，1 个用于最后的输出转换
        self.linears = clones(nn.Linear(d_model, d_model), 4)
        # 用于存储注意力权重得分，方便后续可视化
        self.attn = None
        self.dropout = nn.Dropout(p=dropout)
        
    def forward(self, query, key, value, mask=None):
        # 给 mask 增加一个维度，确保它能同时应用到所有 h 个头上
        if mask is not None:
            mask = mask.unsqueeze(1)
        nbatches = query.size(0) # 获取 Batch 大小（一次处理多少个句子）
        
		# 1. 映射与拆分：将输入的Q,K,V向量分别通过线性层W_q/W_k/W_v(三个参数矩阵), 得到QKV矩阵, 并“切”成 h 个头
        # 维度变化：(Batch, SeqLen, 512) -> (Batch, SeqLen, 8, 64) -> (Batch, 8, SeqLen, 64)
        query, key, value = \
            [l(x).view(nbatches, -1, self.h, self.d_k).transpose(1, 2)
             for l, x in zip(self.linears, (query, key, value))]
        # 2. 批量计算注意力：调用之前定义的 attention 函数
        # 此时是在 8 个头上并行计算，互不干扰
        x, self.attn = attention(query, key, value, mask=mask, 
                                 dropout=self.dropout)
        # 3. 合并 (Concat)：把 8 个头的结果重新拼回 512 维
        # .transpose(1, 2) 把头维度换回去，.contiguous() 整理内存，.view 压扁维度
        x = x.transpose(1, 2).contiguous() \
             .view(nbatches, -1, self.h * self.d_k)    
        # 4. 最后通过最后一个线性层进行整合输出
        return self.linears[-1](x)
```

> **线性层到底做了什么**：这里定义了 4 个线性层
>
> - 前 3 个：分别对应 $W_Q, W_K, W_V$。
> - 第 4 个：对应 $W_O$（输出变换），用来在多头合并后做最后的整合。
>
> 至于矩阵里到底是 $0.1$ 还是 $0.9$？ 那是“训练”阶段的事情。在“定义模型”阶段，你就是一个**架构师**，你只需要设计好：数据从哪里进入线性层，变换后又该流向哪个注意力函数。
>
> 写下 `nn.Linear(d_model, d_model)` 时，PyTorch 会自动做两件事：
>
> - **随机初始化**：它会随机生成一个 $512 \times 512$ 的矩阵（里面的数字可能是 $0.012, -0.054$ 等）。
> - **注册参数**：它把这个矩阵标记为“待学习”。在训练（Training）过程中，模型会根据翻译得准不准，利用**反向传播算法**去微调这些数字。
>
> **你的任务：** 只要确保“输入向量”和“线性层矩阵”的**维度能对上**（比如都是 512），数学上的矩阵乘法就能跑通。
>
> **输入**：是原始的向量 $x$。
>
> **动作**：调用 `l(x)` 让它钻过线性层。
>
> **结果**：出来后的 $x$ 已经变成了具备特定功能的 $Q, K, V$ 矩阵。

multi-head attention在Transformer中有三种不同的使用方式：                                                        

- 在encoder-decoder attention层中，queries来自前面的decoder层，而keys和values来自encoder的输出。这使得decoder中的每个位置都能关注到输入序列中的所有位置。这是模仿序列到序列模型中典型的编码器—解码器的attention机制


- encoder包含self-attention层。在self-attention层中，所有key，value和query来自同一个地方，即encoder中前一层的输出。在这种情况下，encoder中的每个位置都可以关注到encoder上一层的所有位置。


- 类似地，decoder中的self-attention层允许decoder中的每个位置都关注decoder层中当前位置之前的所有位置（包括当前位置）。 为了保持解码器的自回归特性，需要防止解码器中的信息向左流动。我们在缩放点积attention的内部，通过屏蔽softmax输入中所有的非法连接值（设置为$-\infty$）实现了这一点。                                                                                                                                                                                                                                                     

## FFN

除了attention子层之外，我们的编码器和解码器中的每个层都包含一个全连接的前馈网络，该网络在每个层的位置相同（都在每个encoder-layer或者decoder-layer的最后）。该前馈网络包括两个线性变换，并在两个线性变换中间有一个ReLU激活函数。

$$\mathrm{FFN}(x)=\max(0, xW_1 + b_1) W_2 + b_2$$                                                                        

尽管两层都是线性变换，但它们在层与层之间使用不同的参数。另一种描述方式是两个内核大小为1的卷积。 输入和输出的维度都是 $d_{\text{model}}=512$, 内层维度是$d_{ff}=2048$。（也就是第一层输入512维,输出2048维；第二层输入2048维，输出512维）


```python
class PositionwiseFeedForward(nn.Module):
    def __init__(self, d_model, d_ff, dropout=0.1):
        super(PositionwiseFeedForward, self).__init__()
        # 第一层线性变换：将维度从 512 扩展到 2048 (d_ff)
        # 就像把信息“展开”，寻找更深层次的特征
        self.w_1 = nn.Linear(d_model, d_ff)
        # 第二层线性变换：将维度从 2048 压缩回 512
        # 提取完特征后，恢复到原始大小，方便后面的层接着算
        self.w_2 = nn.Linear(d_ff, d_model)
        # 防止过拟合的随机丢弃层
        self.dropout = nn.Dropout(dropout)

    def forward(self, x): # 数据加工流程
        return self.w_2(self.dropout(F.relu(self.w_1(x))))
   		# 1. self.w_1(x): 先投影到高维空间 (2048)
        # 2. F.relu(...): 激活函数，增加非线性（赋予了模型处理复杂逻辑的能力）
        # 3. self.dropout(...): 随机“关掉”一些神经元
        # 4. self.w_2(...): 把数据投影回原始维度 (512)
```

> **位置无关 (Position-wise)**： 这个 FFN 对句子中的每一个单词都是**独立**使用的。比如句子有 10 个词，这 10 个词会分别钻过这套 `w_1 -> ReLU -> w_2` 的管道。它们用的参数矩阵是一模一样的。

## Embeddings

- **嵌入层（Embedding Layer）**：  将输入token和输出token转换为$d_{\text{model}}$维的向量


```python
class Embeddings(nn.Module):
    def __init__(self, d_model, vocab):
        super(Embeddings, self).__init__()
        self.lut = nn.Embedding(vocab, d_model)
        # nn.Embedding 是一个巨大的查找表（Look-Up Table, lut）
        # vocab: 词典大小（比如 30000 个词）
        # d_model: 每个词要转换成的向量维度（比如 512）
        self.d_model = d_model # 保存维度大小，用于后面的数学缩放

    def forward(self, x): # 数据的转换流程
        return self.lut(x) * math.sqrt(self.d_model)
    	# 1. self.lut(x): 将单词的 ID（如 512 号词）换成 512 维的向量
        # 2. * math.sqrt(self.d_model): 将得到的向量乘以维度开方（√512 ≈ 22.6）
```

> **为什么要乘以 `math.sqrt(d_model)`？**
>
> 在后面的代码中，我们会往这些 Embedding 向量里加上“位置编码”（Positional Encoding）。位置编码的值通常比较小。如果我们不把原始的 Embedding 向量**放大**（乘以 $\sqrt{512}$），位置信息就会把语义信息“淹没”掉。

### 位置编码

- **作用**：为了让模型知道单词的顺序，我们必须给每个词打上一个位置编码（序列中token的相对或者绝对位置的信息）                              

  > **如果是 RNN（循环神经网络）**：它是一个词一个词读的，天生就知道谁先谁后。
  >
  > **如果是 Transformer**：它像一张照片一样，通过注意力机制**一次性**看所有的词

- **做法**：将“位置编码”添加到编码器和解码器堆栈底部的输入embeddinng中。位置编码和embedding的维度相同，也是$d_{\text{model}}$ , 所以这两个向量可以相加。

- **类型**：有多种位置编码可以选择，例如通过学习得到的位置编码和固定的位置编码。

  在这项工作中，我们使用不同频率的正弦和余弦函数：                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           

  $$PE_{(pos,2i)} = sin(pos / 10000^{2i/d_{\text{model}}})$$

  $$PE_{(pos,2i+1)} = cos(pos / 10000^{2i/d_{\text{model}}})$$ 

  > 其中$pos$ 是位置，$i$ 是维度。位置编码的每个维度对应于一个正弦曲线。 
  >
  > 选择这个函数是因为它有一个神奇的特性：$PE_{pos+k}$ 可以由 $PE_{pos}$ 线性表示。
  >
  > 通俗理解：这就好比钟表。秒针转一圈，分针动一格；分针转一圈，时针动一格。模型只要看到这些正弦波的相对相位，就能轻易地计算出两个词之间到底隔了多远。

  此外，我们会将编码器和解码器堆栈中的embedding和位置编码的和再加一个dropout。对于基本模型，我们使用的dropout比例是$P_{drop}=0.1$。  

- **实现位置编码（PE）功能** 

```python
class PositionalEncoding(nn.Module): 
    def __init__(self, d_model, dropout, max_len=5000):
        super(PositionalEncoding, self).__init__()
        # 定义 Dropout 层，加完位置编码后进行一次 Dropout
        self.dropout = nn.Dropout(p=dropout)
        
        # 1. 初始化一个全 0 的矩阵，形状是 [5000, 512]
        # 代表最大能处理 5000 个词，每个词有 512 维位置特征
        pe = torch.zeros(max_len, d_model)
        
        # 2. 生成位置索引列 position: [[0], [1], [2], ..., [4999]]
        position = torch.arange(0, max_len).unsqueeze(1)
        
        # 3. 计算公式中的分母项（使用 log 空间计算是为了数值稳定性）
        # 这对应公式里的 10000^{2i/d_model}
        div_term = torch.exp(torch.arange(0, d_model, 2) *
                             -(math.log(10000.0) / d_model))
        # 4. 根据公式，偶数维度(0, 2, 4...)使用正弦 sin
        pe[:, 0::2] = torch.sin(position * div_term)
        # 5. 奇数维度(1, 3, 5...)使用余弦 cos
        pe[:, 1::2] = torch.cos(position * div_term)
        # 6. 增加一个 batch 维度，变成 [1, 5000, 512]，方便后续直接和输入相加
        pe = pe.unsqueeze(0)
        # 7. 【关键】register_buffer 告诉 PyTorch：这个 pe 矩阵是模型的一部分，但它不是“参数”，不需要通过反向传播来更新
        self.register_buffer('pe', pe)
        
    def forward(self, x): # 将位置编码直接加到 Embedding 向量上
        x = x + Variable(self.pe[:, :x.size(1)], 
                         requires_grad=False)
        # x 是词嵌入 [Batch, SeqLen, 512]
        # 我们只截取和当前输入句子长度一致的那一段位置编码
        # Variable 包装是为了兼容旧版代码，requires_grad=False 再次强调不参与训练
        return self.dropout(x) # 返回经过 Dropout 的结果
```



## 完整模型

- `make_model` ：全自动组装工厂，告诉工厂你要造一个多大规模的模型。

  它把所有零件（编码器、解码器、注意力机制、嵌入层等）按照图纸全部拼装在一起。

  > **`src_vocab`** 源语言的词典大小；**`tgt_vocab`** 目标语言的词典大小
  >
  > **`N=6`**：堆叠层数。编码器叠 6 层，解码器也叠 6 层
  >
  > **`d_model=512`**：所有单词向量进入模型后，统一变成 512 维
  >
  > **`d_ff=2048`**：前馈网络中间临时扩大的维度
  >
  > **`h=8`**：多头注意力的头数。把 512 维拆成 8 份，每份 64 维
  >
  > **`dropout=0.1`**：训练时的“丢弃率”，随机关掉 10% 的神经元防止死记硬背


```python
def make_model(src_vocab, tgt_vocab, N=6, 
               d_model=512, d_ff=2048, h=8, dropout=0.1):
    # 1. 准备工具：c 是深拷贝的缩写，后续调用它让每个层都是独立的副本
    c = copy.deepcopy
    # 2. 初始化基础组件（原材料）
    attn = MultiHeadedAttention(h, d_model) # 创建多头注意力实例
    ff = PositionwiseFeedForward(d_model, d_ff, dropout) # 创建前馈网络实例
    position = PositionalEncoding(d_model, dropout) # 创建位置编码实例
    # 3. 核心组装：构建 EncoderDecoder 整体架构
    model = EncoderDecoder(
		# 组装编码器：包含 N 层具体的 EncoderLayer
        Encoder(EncoderLayer(d_model, c(attn), c(ff), dropout), N),
        # 组装解码器：包含 N 层具体的 DecoderLayer
        Decoder(DecoderLayer(d_model, c(attn), c(attn), c(ff), dropout), N),
        # 源语言输入链：先做词嵌入，再加位置编码（nn.Sequential 是按顺序执行的容器）
        nn.Sequential(Embeddings(d_model, src_vocab), c(position)),
        # 目标语言输入链：先做词嵌入，再加位置编码
        nn.Sequential(Embeddings(d_model, tgt_vocab), c(position)),
        # 最后接上生成器（嘴巴），输出单词概率
        Generator(d_model, tgt_vocab))
    
	# 4. 参数初始化（给零件上油）
    # 遍历模型中所有大于 1 维的参数矩阵（如线性层的权重）
    for p in model.parameters():
        if p.dim() > 1:
            # 使用 Xavier 初始化（也叫 Glorot 初始化）
            # 这种方法能让模型在刚开始训练时，各层的信号强度保持稳定，不至于消失或爆炸
            nn.init.xavier_uniform(p)
    return model
```

> - `Encoder(EncoderLayer(d_model, c(attn), c(ff), dropout), N)`
>   - `c` 就是 `copy.deepcopy`（深拷贝）。
>   - `attn` 是之前已经创建的多头注意力层实例，通过 `c(attn)` 给每一层都克隆一个完全独立的新的注意力层；`ff` 同理，`c(ff)` 是一个克隆的新 FFN 层。
>   - **`EncoderLayer(...)`**：把这两个克隆体装进一个编码器里。
>   - **`Encoder(..., N)`**：把这个编码器克隆 N 次，组合成 N 层的编码器整体。
>
> - `nn.Sequential(Embeddings(d_model, src_vocab), c(position))`
>
>   - `nn.Sequential` 是一个容器，它会按照你放进去的顺序，**依次**执行里面的任务。
>
>   - **工人 A (`Embeddings`)**：负责把单词 ID 变成 512 维的向量。
>
>     **工人 B (`c(position)`)**：负责给这些向量加上位置信息（正弦波）。
>
>     **`c(position)`**：这里的 `c` 是 `deepcopy`（深拷贝）。因为源语言（中文）和目标语言（英文）都需要位置编码，所以克隆了一个副本给源语言流水线。


```python
# Small example model.
tmp_model = make_model(10, 10, 2)
None
```


# 训练

本节描述了我们模型的训练机制。

> 我们在这快速地介绍一些工具，这些工具用于训练一个标准的encoder-decoder模型。首先，我们定义一个批处理对象，其中包含用于训练的 src 和目标句子，以及构建掩码。

## 批处理和掩码

- 在训练 Transformer 时，有两个大麻烦需要处理：
  1. **对齐问题**：一句话长，一句话短，我们要用 `pad`（填充符，通常是 0）把它们补成一样长。但模型不应该去“学习”这些填充符。
  2. **错位预测**：训练时，我们要用“当前的词”去预测“下一个词”。这就需要把目标句子（Target）切成两半：一半给模型看，一半用来当标准答案。
- **Batch类**：训练期间持有带掩码的数据批次对象


```python
class Batch:
    def __init__(self, src, trg=None, pad=0):
        # 1. 保存源语言句子（如中文）
        self.src = src
        # 2. 生成源语言掩码。只要不是pad的地方就是1，否则是0（告诉模型别去关注那些为了对齐而补的0）
        self.src_mask = (src != pad).unsqueeze(-2)
        
        if trg is not None: # 如果非空
            # 3. self.trg: 给解码器输入的“问题”, 取除了最后一个词的所有词（开始符号 + 文本内容）
            self.trg = trg[:, :-1]
            
            # 4. self.trg_y: 期望模型输出的“正确答案”,取除了第一个词（开始符号）的所有词, 这样 trg 和 trg_y 就在位置上一一对应了: 看到第 i 个词，预测第 i+1 个词
            self.trg_y = trg[:, 1:]
            
            # 5. 生成目标语言掩码, 既要遮住pad, 又要遮住“未来的单词”
            self.trg_mask = self.make_std_mask(self.trg, pad)
            
            # 6. 计算这一批次中实际有多少个有效的单词(非pad),用于后面计算平均损失Loss
            self.ntokens = (self.trg_y != pad).data.sum()
    
    @staticmethod
    def make_std_mask(tgt, pad): # 创建遮住 padding 和 未来单词的复合掩码
        # 先遮住 pad
        tgt_mask = (tgt != pad).unsqueeze(-2)
        # 再用 & (与运算) 结合我们之前讲过的“三角形” subsequent_mask
        # 只有“既不是 pad”且“不是未来”的位置才设为 1
        tgt_mask = tgt_mask & Variable(
            subsequent_mask(tgt.size(-1)).type_as(tgt_mask.data))
        return tgt_mask
```

> - `self.src_mask = (src != pad).unsqueeze(-2)`
>
>   - `(src != pad)`：生成布尔掩码，是 pad 的时候返回 False
>
>   - `.unsqueeze(-2)`：增加维度，`-2` 代表倒数第二维。
>
>     Transformer 的注意力机制要求掩码的形状必须是 `[Batch, 1, 长度]`。
>
>     原本的掩码是 `[Batch, 长度]`，在倒数第二维增加一维，就变成了 `[Batch, 1, 长度]`。
>
> - `self.trg = trg[:, :-1]`：矩阵切片/索引操作
>
>   假设 `trg` 是一个二维矩阵 `[行, 列]`：
>
>   - **`:`**：取全部。在逗号左边，代表**取所有的行**（即这一批次里所有的句子）。
>
>   - **`, `**：分隔维度。左边是行，右边是列
>
>   - **`:-1`**：从开始取到倒数第一个（但不包括最后一个）
>
>     比如句子是 `[A, B, C, D]`，`:-1` 拿到的就是 `[A, B, C]`。
>
>   - **`1:`**：从索引 1 开始取到最后
>
>     比如句子是 `[A, B, C, D]`，`1:` 拿到的就是 `[B, C, D]`。

## Training Loop

标准的训练和日志记录函数，批处理（Batch Processing）的任务调度器


```python
def run_epoch(data_iter, model, loss_compute):
    start = time.time()      # 记录开始时间
    total_tokens = 0         # 总单词数（用于算平均损失）
    total_loss = 0           # 总损失
    tokens = 0               # 临时计数，用于计算每秒处理速度
    
    for i, batch in enumerate(data_iter):
        # 1. 执行前向传播：拿到编码器-解码器的输出
        # 输入：原文、错位后的译文、原文掩码、译文掩码
        out = model.forward(batch.src, batch.trg, 
                            batch.src_mask, batch.trg_mask)
        # 2. 计算损失：loss_compute 既计算了 Loss，也顺便更新了梯度（如果是训练模式）
        # 参数：模型输出、标准答案(trg_y)、本批次有效单词数
        loss = loss_compute(out, batch.trg_y, batch.ntokens)
        # 3. 统计数据
        total_loss += loss
        total_tokens += batch.ntokens
        tokens += batch.ntokens
        # 4. 每 50 个批次打印一次进度
        if i % 50 == 1:
            elapsed = time.time() - start
            # 打印：当前步数，平均每个词的 Loss，每秒处理的单词量
            print("Epoch Step: %d Loss: %f Tokens per Sec: %f" %
                    (i, loss / batch.ntokens, tokens / elapsed))
            start = time.time()  # 重置计时
            tokens = 0           # 重置单词计数
            
    # 返回这一整圈跑完后的平均损失
    return total_loss / total_tokens
```

## 训练数据和批处理
&#8195;&#8195;我们在包含约450万个句子对的标准WMT 2014英语-德语数据集上进行了训练。这些句子使用字节对编码进行编码，源语句和目标语句共享大约37000个token的词汇表。对于英语-法语翻译，我们使用了明显更大的WMT 2014英语-法语数据集，该数据集由 3600 万个句子组成，并将token拆分为32000个word-piece词表。<br>
每个训练批次包含一组句子对，句子对按相近序列长度来分批处理。每个训练批次的句子对包含大约25000个源语言的tokens和25000个目标语言的tokens。

> 我们将使用torch text进行批处理（后文会进行更详细地讨论）。在这里，我们在torchtext函数中创建批处理，以确保我们填充到最大值的批处理大小不会超过阈值（如果我们有8个gpu，则为25000）。


```python
global max_src_in_batch, max_tgt_in_batch
def batch_size_fn(new, count, sofar):
    "Keep augmenting batch and calculate total number of tokens + padding."
    global max_src_in_batch, max_tgt_in_batch
    if count == 1:
        max_src_in_batch = 0
        max_tgt_in_batch = 0
    max_src_in_batch = max(max_src_in_batch,  len(new.src))
    max_tgt_in_batch = max(max_tgt_in_batch,  len(new.trg) + 2)
    src_elements = count * max_src_in_batch
    tgt_elements = count * max_tgt_in_batch
    return max(src_elements, tgt_elements)
```

## 硬件和训练时间
我们在一台配备8个 NVIDIA P100 GPU 的机器上训练我们的模型。使用论文中描述的超参数的base models，每个训练step大约需要0.4秒。我们对base models进行了总共10万steps或12小时的训练。而对于big models，每个step训练时间为1.0秒，big models训练了30万steps（3.5 天）。

## Optimizer

我们使用Adam优化器[(cite)](https://arxiv.org/abs/1412.6980)，其中 $\beta_1=0.9$, $\beta_2=0.98$并且$\epsilon=10^{-9}$。我们根据以下公式在训练过程中改变学习率：                                         
$$
lrate = d_{\text{model}}^{-0.5} \cdot                                                                                                                                                                                                                                                                                                
  \min({step\_num}^{-0.5},                                                                                                                                                                                                                                                                                                  
    {step\_num} \cdot {warmup\_steps}^{-1.5})                                                                                                                                                                                                                                                                               
$$
这对应于在第一次$warmup\_steps$步中线性地增加学习速率，并且随后将其与步数的平方根成比例地减小。我们使用$warmup\_steps=4000$。                            

> 注意：这部分非常重要。需要使用此模型设置进行训练。


```python

class NoamOpt:
    "Optim wrapper that implements rate."
    def __init__(self, model_size, factor, warmup, optimizer):
        self.optimizer = optimizer
        self._step = 0
        self.warmup = warmup
        self.factor = factor
        self.model_size = model_size
        self._rate = 0
        
    def step(self):
        "Update parameters and rate"
        self._step += 1
        rate = self.rate()
        for p in self.optimizer.param_groups:
            p['lr'] = rate
        self._rate = rate
        self.optimizer.step()
        
    def rate(self, step = None):
        "Implement `lrate` above"
        if step is None:
            step = self._step
        return self.factor * \
            (self.model_size ** (-0.5) *
            min(step ** (-0.5), step * self.warmup ** (-1.5)))
        
def get_std_opt(model):
    return NoamOpt(model.src_embed[0].d_model, 2, 4000,
            torch.optim.Adam(model.parameters(), lr=0, betas=(0.9, 0.98), eps=1e-9))
```


> 以下是此模型针对不同模型大小和优化超参数的曲线示例。


```python
# Three settings of the lrate hyperparameters.
opts = [NoamOpt(512, 1, 4000, None), 
        NoamOpt(512, 1, 8000, None),
        NoamOpt(256, 1, 4000, None)]
plt.plot(np.arange(1, 20000), [[opt.rate(i) for opt in opts] for i in range(1, 20000)])
plt.legend(["512:4000", "512:8000", "256:4000"])
None
```





## 正则化
### 标签平滑

在训练过程中，我们使用的label平滑的值为$\epsilon_{ls}=0.1$ [(cite)](https://arxiv.org/abs/1512.00567)。虽然对label进行平滑会让模型困惑，但提高了准确性和BLEU得分。

> 我们使用KL div损失实现标签平滑。我们没有使用one-hot独热分布，而是创建了一个分布，该分布设定目标分布为1-smoothing，将剩余概率分配给词表中的其他单词。


```python
class LabelSmoothing(nn.Module):
    "Implement label smoothing."
    def __init__(self, size, padding_idx, smoothing=0.0):
        super(LabelSmoothing, self).__init__()
        self.criterion = nn.KLDivLoss(size_average=False)
        self.padding_idx = padding_idx
        self.confidence = 1.0 - smoothing
        self.smoothing = smoothing
        self.size = size
        self.true_dist = None
        
    def forward(self, x, target):
        assert x.size(1) == self.size
        true_dist = x.data.clone()
        true_dist.fill_(self.smoothing / (self.size - 2))
        true_dist.scatter_(1, target.data.unsqueeze(1), self.confidence)
        true_dist[:, self.padding_idx] = 0
        mask = torch.nonzero(target.data == self.padding_idx)
        if mask.dim() > 0:
            true_dist.index_fill_(0, mask.squeeze(), 0.0)
        self.true_dist = true_dist
        return self.criterion(x, Variable(true_dist, requires_grad=False))
```

下面我们看一个例子，看看平滑后的真实概率分布。


```python
#Example of label smoothing.
crit = LabelSmoothing(5, 0, 0.4)
predict = torch.FloatTensor([[0, 0.2, 0.7, 0.1, 0],
                             [0, 0.2, 0.7, 0.1, 0], 
                             [0, 0.2, 0.7, 0.1, 0]])
v = crit(Variable(predict.log()), 
         Variable(torch.LongTensor([2, 1, 0])))

# Show the target distributions expected by the system.
plt.imshow(crit.true_dist)
None
```

    /Users/niepig/Desktop/zhihu/learn-nlp-with-transformers/venv/lib/python3.8/site-packages/torch/nn/_reduction.py:42: UserWarning: size_average and reduce args will be deprecated, please use reduction='sum' instead.
      warnings.warn(warning.format(ret))




![svg](2.2.1-Pytorch%E7%BC%96%E5%86%99Transformer_files/2.2.1-Pytorch%E7%BC%96%E5%86%99Transformer_73_1.svg)
    



```python
print(crit.true_dist)
```

    tensor([[0.0000, 0.1333, 0.6000, 0.1333, 0.1333],
            [0.0000, 0.6000, 0.1333, 0.1333, 0.1333],
            [0.0000, 0.0000, 0.0000, 0.0000, 0.0000]])


由于标签平滑的存在，如果模型对于某个单词特别有信心，输出特别大的概率，会被惩罚。如下代码所示，随着输入x的增大，x/d会越来越大，1/d会越来越小，但是loss并不是一直降低的。


```python
crit = LabelSmoothing(5, 0, 0.1)
def loss(x):
    d = x + 3 * 1
    predict = torch.FloatTensor([[0, x / d, 1 / d, 1 / d, 1 / d],
                                 ])
    #print(predict)
    return crit(Variable(predict.log()),
                 Variable(torch.LongTensor([1]))).item()

y = [loss(x) for x in range(1, 100)]
x = np.arange(1, 100)
plt.plot(x, y)

```




    [<matplotlib.lines.Line2D at 0x7f7fad46c970>]




​    
![svg](2.2.1-Pytorch%E7%BC%96%E5%86%99Transformer_files/2.2.1-Pytorch%E7%BC%96%E5%86%99Transformer_76_1.svg)
​    


# 实例

> 我们可以从尝试一个简单的复制任务开始。给定来自小词汇表的一组随机输入符号symbols，目标是生成这些相同的符号。

## 合成数据


```python
def data_gen(V, batch, nbatches):
    "Generate random data for a src-tgt copy task."
    for i in range(nbatches):
        data = torch.from_numpy(np.random.randint(1, V, size=(batch, 10)))
        data[:, 0] = 1
        src = Variable(data, requires_grad=False)
        tgt = Variable(data, requires_grad=False)
        yield Batch(src, tgt, 0)
```

## 损失函数计算


```python
class SimpleLossCompute:
    "A simple loss compute and train function."
    def __init__(self, generator, criterion, opt=None):
        self.generator = generator
        self.criterion = criterion
        self.opt = opt
        
    def __call__(self, x, y, norm):
        x = self.generator(x)
        loss = self.criterion(x.contiguous().view(-1, x.size(-1)), 
                              y.contiguous().view(-1)) / norm
        loss.backward()
        if self.opt is not None:
            self.opt.step()
            self.opt.optimizer.zero_grad()
        return loss.item() * norm
```

## 贪婪解码


```python
# Train the simple copy task.
V = 11
criterion = LabelSmoothing(size=V, padding_idx=0, smoothing=0.0)
model = make_model(V, V, N=2)
model_opt = NoamOpt(model.src_embed[0].d_model, 1, 400,
        torch.optim.Adam(model.parameters(), lr=0, betas=(0.9, 0.98), eps=1e-9))

for epoch in range(10):
    model.train()
    run_epoch(data_gen(V, 30, 20), model, 
              SimpleLossCompute(model.generator, criterion, model_opt))
    model.eval()
    print(run_epoch(data_gen(V, 30, 5), model, 
                    SimpleLossCompute(model.generator, criterion, None)))
```

> 为了简单起见，此代码使用贪婪解码来预测翻译。


```python
def greedy_decode(model, src, src_mask, max_len, start_symbol):
    memory = model.encode(src, src_mask)
    ys = torch.ones(1, 1).fill_(start_symbol).type_as(src.data)
    for i in range(max_len-1):
        out = model.decode(memory, src_mask, 
                           Variable(ys), 
                           Variable(subsequent_mask(ys.size(1))
                                    .type_as(src.data)))
        prob = model.generator(out[:, -1])
        _, next_word = torch.max(prob, dim = 1)
        next_word = next_word.data[0]
        ys = torch.cat([ys, 
                        torch.ones(1, 1).type_as(src.data).fill_(next_word)], dim=1)
    return ys

model.eval()
src = Variable(torch.LongTensor([[1,2,3,4,5,6,7,8,9,10]]) )
src_mask = Variable(torch.ones(1, 1, 10) )
print(greedy_decode(model, src, src_mask, max_len=10, start_symbol=1))
```

    tensor([[ 1,  2,  3,  4,  5,  6,  7,  8,  9, 10]])


# 真实场景示例
由于原始jupyter的真实数据场景需要多GPU训练，本教程暂时不将其纳入，感兴趣的读者可以继续阅读[原始教程](https://nlp.seas.harvard.edu/2018/04/03/attention.html)。另外由于真实数据原始url失效，原始教程应该也无法运行真实数据场景的代码。


<noscript>Please enable JavaScript to view the <a href="https://disqus.com/?ref_noscript" rel="nofollow">comments powered by Disqus.</a></noscript>
