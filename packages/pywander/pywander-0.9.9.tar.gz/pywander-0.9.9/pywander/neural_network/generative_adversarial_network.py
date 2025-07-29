import torch
import torch.nn as nn
import random

import pandas

import matplotlib.pyplot as plt


def generate_real():
    real_data = torch.FloatTensor([
        random.uniform(0.9, 1.0),
        random.uniform(0.0, 0.1),
        random.uniform(0.9, 1.0),
        random.uniform(0.0, 0.1)
    ])
    return real_data


def generate_random(size):
    random_data = torch.rand(size)
    return random_data


from pywander.neural_network.general import NeuralNetwork


class Sensor(NeuralNetwork):
    """
    一般感知器
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Operator(NeuralNetwork):
    """
    一般行动器
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ReplacerO(NeuralNetwork):
    """
    GAN网络架构 替换器O 存储的是知觉信息 实现 Op1->Op2

    复杂网络架构的训练首先要判断谁对谁错，只有错的那些网络节点才会被训练
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ReplacerS(NeuralNetwork):
    """
    替换器S 存储的是行动信息 实现S1-> S2
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Discriminator(NeuralNetwork):
    """
    鉴别器
    op = 1 表示特征检测存在
    op = 0 表示特征检测不存在
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.model = nn.Sequential(
            nn.Linear(self.in_features, 3),
            nn.Sigmoid(),
            nn.Linear(3, self.out_features),
            nn.Sigmoid()
        )
        self.loss_function = nn.MSELoss()
        self.optimizer = torch.optim.SGD(self.parameters(), lr=0.01)


class Generator(NeuralNetwork):
    """
    生成器
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.model = nn.Sequential(
            nn.Linear(self.in_features, 3),
            nn.Sigmoid(),
            nn.Linear(3, self.out_features),
            nn.Sigmoid()
        )
        self.optimizer = torch.optim.SGD(self.parameters(), lr=0.01)


class GAN(NeuralNetwork):
    """
    GAN网络
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if kwargs.get('data_features'):
            self.data_features = kwargs.get('data_features')

        self.discriminator = Discriminator(in_features=self.data_features, out_features=1)
        self.generator = Generator(in_features=1, out_features=self.data_features)

    def train_one(self, inputs, targets):
        """
        targets 真实数据对应的标签值 比如1
        默认虚假数据对应的标签值为0 最终要实现的是从0到1的概率均等
        """
        self.train()
        inputs, targets = inputs.to(self.device), targets.to(self.device)
        true_data = inputs
        fake_input = torch.rand(1).to(self.device)

        # step1 训练鉴别器 真实数据-真实标签
        self.discriminator.train_one(true_data, targets)
        # step2 训练鉴别器 虚假数据-虚假标签
        self.discriminator.train_one(self.generator.forward(fake_input).detach(),
                                     torch.FloatTensor([0.0]).to(self.device))

        # step3 训练生产器 虚假数据-真实标签
        g_output = self.generator.forward(fake_input)
        d_output = self.discriminator.forward(g_output)
        loss = self.discriminator.loss_function(d_output, targets)
        # 只用生产器的优化器更新自身权重参数来达到逼近鉴别器预期的数据概率分布
        self.generator.optimizer.zero_grad()
        loss.backward()
        self.generator.optimizer.step()


class DiscriminatorExclusiveGroup(NeuralNetwork):
    """
    鉴别器独占集群

    如果算力有限，那么鉴别器集群
    op = 1 可能存在鉴别器集群的某个特征
    op = 0 鉴别器集群的所有特征都不存在
    在算力有限的情况下，鉴别器集群是一种模糊处理
    ----------------------------------
    在算力充沛的情况下
    op = 0 所有特征都不存在 子鉴别器针对 input-0 训练数据全部要各自训练
    op = 1 如果某个训练数据明确属于某个子特征，目标子鉴别器以1进行训练，其余鉴别器以0进行训练
    ----------------------------------

    """


if __name__ == '__main__':
    discriminator = Discriminator(in_features=4, out_features=1)

    for i in range(10000):
        # op=1
        discriminator.train_one(generate_real(), torch.FloatTensor([1.0]))
        # op=0
        discriminator.train_one(generate_random(4), torch.FloatTensor([0.0]))
