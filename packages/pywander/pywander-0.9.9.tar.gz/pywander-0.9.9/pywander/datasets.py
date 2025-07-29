import os

import pandas as pd
import torch
from torch.utils.data import Dataset
from torchvision import datasets as torchvision_datasets
from torchvision.transforms import ToTensor

from pywander.path import normalized_path
from pywander.utils.plot_utils import image_plot


def get_datasets_folder(app_name='test'):
    """
    获取数据集文件夹路径
    """
    path = normalized_path(os.path.join('~', 'Pywander', app_name, 'datasets'))

    return path


def get_datasets_path(*args, app_name='test'):
    """
    获取数据集文件路径
    """
    if not args:
        raise Exception('please input the dataset filename.')

    folder_path = get_datasets_folder(app_name=app_name)

    path = os.path.join(folder_path, *args)

    if not os.path.exists(path):
        raise Exception(f'file not exists: {path}')

    if not os.path.isfile(path):
        raise Exception(f'can not find the file: {path}')

    return path


def _load_mnist_csv_data(*args, line_count=-1):
    """
    train_data: https://pjreddie.com/media/files/mnist_train.csv
    test_data: https://pjreddie.com/media/files/mnist_test.csv

    灰度图现在定义是0为黑，255为白，从黑到白为从0到255的整数值。
    mnist里面的数据是个反的，为了和现代灰度图标准统一，最好将mnist的图片数据预处理下。
    """
    file_path = get_datasets_path(*args)

    if line_count < 0:
        line_count = None

    df = pd.read_csv(file_path, nrows=line_count, header=None)

    for c in range(1, 785):
        df[c] = 255 - df[c]

    return df


def load_mnist_csv_data(*args, line_count=-1):
    """
    train_data: https://pjreddie.com/media/files/mnist_train.csv
    test_data: https://pjreddie.com/media/files/mnist_test.csv

    灰度图现在定义是0为黑，255为白，从黑到白为从0到255的整数值。
    mnist里面的数据是个反的，为了和现代灰度图标准统一，最好将mnist的图片数据预处理下。
    """
    df = _load_mnist_csv_data(*args, line_count=line_count)

    for index, row in df.iterrows():
        label = row[0]
        value = row[1:].to_numpy('float')
        yield label, value


def load_mnist_train_data(line_count=-1):
    return load_mnist_csv_data('mnist', 'mnist_train.csv', line_count=line_count)


def load_mnist_test_data(line_count=-1):
    return load_mnist_csv_data('mnist', 'mnist_test.csv', line_count=line_count)


def plot_mnist_image(image_data, label, ax=None, **kwargs):
    if ax is None:
        import matplotlib.pyplot as plt
        ax = plt.gca()

    image_data = image_data.reshape(28, 28)
    title = f"label = {label}"
    image_plot(ax, image_data, title=title, cmap='gray', interpolation='none', **kwargs)


class FashionMNIST(torchvision_datasets.FashionMNIST):
    def __init__(self, train: bool = True) -> None:
        super().__init__(get_datasets_folder(), train=train, transform=ToTensor())


class MnistDataset(Dataset):
    def __init__(self, train=True, line_count=-1):
        if train:
            self.df = _load_mnist_csv_data('mnist', 'mnist_train.csv', line_count=line_count)
        else:
            self.df = _load_mnist_csv_data('mnist', 'mnist_test.csv', line_count=line_count)

    def __len__(self):
        return len(self.df)

    def __getitem__(self, index):
        value = self.df.iloc[index, 1:].to_numpy(dtype='float') / 255.0
        sample = torch.FloatTensor(value)

        label = self.df.iloc[index, 0]
        target = torch.zeros(10)
        target[label] = 1.0
        return sample, target

    def plot_image(self, index, ax=None):
        value = self.df.iloc[index, 1:].to_numpy(dtype='float')
        label = self.df.iloc[index, 0]

        plot_mnist_image(value, label, ax=ax)
