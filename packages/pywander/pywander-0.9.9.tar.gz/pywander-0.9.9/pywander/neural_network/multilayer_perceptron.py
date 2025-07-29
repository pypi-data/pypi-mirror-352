import torch
import torch.nn as nn

from pywander.neural_network.general import NeuralNetwork


class SimpleMLP(NeuralNetwork):
    """
    单隐藏层感知机
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = nn.Sequential(
            nn.Linear(self.in_features, 200),
            nn.Sigmoid(),
            nn.Linear(200, self.out_features),
            nn.Sigmoid()
        )

        self.loss_function = nn.MSELoss()
        self.optimizer = torch.optim.SGD(self.parameters(), lr=0.01)


class SimpleMLP2(NeuralNetwork):
    """
    对简单单隐藏层感知机进行一些改良
    BCELoss 更适合分类任务 只能处理0-1的数值 需要加一个Sigmoid层
    线性整流函数  ReLU
    带泄露线性整流函数 Leaky ReLU 比ReLU在负数上表现稍好
    LayerNorm 归一化层 在进入下一层神经网络进行归一化处理可以提升网络性能
    Adam优化器 会自适应调整学习率 增加动量来避免陷入局部最小值 表现一般比SGD好
    批次训练提升训练效率 多次训练
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = nn.Sequential(
            nn.Linear(self.in_features, 200),
            nn.LeakyReLU(0.02),
            nn.LayerNorm(200),
            nn.Linear(200, self.out_features),
            nn.Sigmoid()
        )

        self.loss_function = nn.BCELoss()
        self.optimizer = torch.optim.Adam(self.parameters())


if __name__ == '__main__':
    def train_simple_mlp():
        from pywander.datasets import MnistDataset

        training_data = MnistDataset(train=True)
        from torch.utils.data import DataLoader

        batch_size = 16
        train_dataloader = DataLoader(training_data, batch_size=batch_size)

        model = SimpleMLP(in_features=28 * 28, out_features=10)
        model.to_device()

        epochs = 3
        for e in range(epochs):
            model.train_batch2(train_dataloader)

        from pywander.models import save_model, load_model

        model = save_model(model, 'mnist', 'simple_mlp.pkl')


    def test_simple_mlp():
        from pywander.datasets import MnistDataset

        test_data = MnistDataset(train=False)
        from torch.utils.data import DataLoader
        batch_size = 16
        test_dataloader = DataLoader(test_data, batch_size=batch_size)

        from pywander.models import save_model, load_model
        model = load_model('mnist', 'simple_mlp.pkl')

        model.test_batch(test_dataloader)


    # train_simple_mlp()
    # test_simple_mlp()

    def train_simple_mlp2():
        from pywander.datasets import MnistDataset

        training_data = MnistDataset(train=True)
        from torch.utils.data import DataLoader

        batch_size = 32
        train_dataloader = DataLoader(training_data, batch_size=batch_size, shuffle=True)

        model = SimpleMLP2(in_features=28 * 28, out_features=10)
        model.to_device()

        epochs = 5
        for e in range(epochs):
            model.train_batch(train_dataloader)

        from pywander.models import save_model, load_model

        model = save_model(model, 'mnist', 'simple_mlp2.pkl')


    def test_simple_mlp2():
        from pywander.datasets import MnistDataset

        test_data = MnistDataset(train=False)
        from torch.utils.data import DataLoader
        batch_size = 32
        test_dataloader = DataLoader(test_data, batch_size=batch_size, shuffle=True)

        from pywander.models import save_model, load_model
        model = load_model('mnist', 'simple_mlp2.pkl')

        model.test_batch(test_dataloader)


    # train_simple_mlp2()
    test_simple_mlp2()
