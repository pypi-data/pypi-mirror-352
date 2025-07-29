"""
本脚本不具有使用价值

出于历史原因保留，可以作为初学者手写神经网络入门的参考。

除非有极高深的数学造诣，否则这样慢慢从简单到复杂，逐步摸索实践的过程是不能跳过去的。
"""

import numpy as np
from scipy.special import expit, logit

from pywander.datasets import load_mnist_test_data, load_mnist_train_data
from pywander.math.linear_algebra import to_row_vector, to_column_vector, row_vector_to_column_vector, minmax_scale

class NeuralNetwork:
    def __init__(self, input_nodes=1, output_nodes=1, learning_rate=0.3, feature_range=(0.01, 0.99)):
        # 权重、信号的值的约束范围
        self.feature_range = feature_range
        # 输入层节点数
        self.i_nodes = input_nodes
        # 输出层节点数
        self.o_nodes = output_nodes
        # label 任何神经网络都有其判断标识 只是有些和外界发生了对齐行为
        # 只有发生对齐行为的神经网络才会有训练行为
        self.label_list = ['' for _ in range(self.o_nodes)]
        self.label_out = []
        self.init_label_out()

        # 学习率
        self.lr = learning_rate

    def init_label_out(self):
        self.label_out = np.eye(self.o_nodes)

    def set_label_list(self, label_list):
        assert len(label_list) == self.o_nodes
        self.label_list = label_list

    def get_label_out(self, label):
        index = self.label_list.index(label)
        return self.label_out[index]

    def train(self, *args, **kwargs):
        pass

    def query(self, input_array):
        pass

    def preprocessing_minmax_scale(self, input_array):
        input_array = minmax_scale(input_array, feature_range=self.feature_range)
        return input_array


class LinearModel(NeuralNetwork):
    """
    单隐藏层前馈神经网络
    无激活函数或者激活函数为 lambda x:x ，本质上仍然为线性模型，模拟能力有限，但深入其细节对于入门学习了解神经网络还是有所帮助的。

    """

    def __init__(self, input_nodes=1, output_nodes=1, hidden_nodes=1, learning_rate=0.3):
        super().__init__(input_nodes=input_nodes, output_nodes=output_nodes, learning_rate=learning_rate)
        # 隐藏层节点数
        self.h_nodes = hidden_nodes

        # 权重矩阵随机生成
        self.weight_matrix_hidden_output = None
        self.weight_matrix_input_hidden = None
        self.init_weight_matrix2()

    def init_weight_matrix(self):
        """
        经过一些实践就会发现初始权重矩阵有一些小技巧和注意事项，然后总的来说不太重要，因此不需要精确
        """
        self.weight_matrix_input_hidden = np.random.rand(self.h_nodes, self.i_nodes) - 0.5
        self.weight_matrix_hidden_output = np.random.rand(self.o_nodes, self.h_nodes) - 0.5

    def pre_process_input2(self, input_array):
        # 输入信号归一化
        norm = np.linalg.norm(input_array)
        input_array = input_array / norm
        return input_array

    def init_weight_matrix2(self):
        """
        以0为中心的正态分布采样
        """
        self.weight_matrix_input_hidden = np.random.normal(
            0.0, pow(self.h_nodes, -0.5), (self.h_nodes, self.i_nodes))
        self.weight_matrix_hidden_output = np.random.normal(
            0.0, pow(self.o_nodes, -0.5), (self.o_nodes, self.h_nodes))

    def query(self, input_array):
        input_array = self.pre_process_input2(input_array)

        hidden_input = np.dot(self.weight_matrix_input_hidden, input_array)
        # hidden_output = self.activation_function(hidden_input)
        hidden_output = hidden_input
        final_inputs = np.dot(self.weight_matrix_hidden_output, hidden_output)
        # final_outputs = self.activation_function(final_inputs)
        final_outputs = final_inputs
        return final_outputs

    def query_label(self, intput_array):
        final_outputs = self.query(intput_array)
        index = np.argmax(final_outputs)
        return self.label_list[index]

    def train(self, input_array, label):
        input_array = self.pre_process_input2(input_array)

        hidden_input = np.dot(self.weight_matrix_input_hidden, input_array)
        # hidden_output = self.activation_function(hidden_input)
        hidden_output = hidden_input
        final_inputs = np.dot(self.weight_matrix_hidden_output, hidden_output)
        # final_outputs = self.activation_function(final_inputs)
        final_outputs = final_inputs

        target_label_out = self.get_label_out(label)
        error_output = target_label_out - final_outputs

        error_hidden = np.dot(self.weight_matrix_hidden_output.transpose(), error_output)

        self.weight_matrix_hidden_output += self.lr * np.dot(to_column_vector(error_output),
                                                             to_row_vector(hidden_output))

        self.weight_matrix_input_hidden += self.lr * np.dot(to_column_vector(error_hidden), to_row_vector(input_array))

    def init_weight_matrix_old(self, init_array):
        """
        初始权重
        """
        column_vector_output = np.array([[1]])
        row_vector_hidden = np.random.rand(self.h_nodes)
        row_vector_hidden = to_row_vector(row_vector_hidden)
        # 隐藏层输出信号归一化 使得modifiers=1
        norm = np.linalg.norm(row_vector_hidden)
        row_vector_hidden = row_vector_hidden / norm
        column_vector_hidden = row_vector_to_column_vector(row_vector_hidden)

        # res = np.dot(row_vector_hidden, row_vector_hidden.transpose())
        # modifiers = res[0][0]

        self.weight_matrix_hidden_output = np.dot(column_vector_output, row_vector_hidden)
        # self.weight_matrix_hidden_output = self.weight_matrix_hidden_output / modifiers

        # 输入信号归一化 使得modifiers=1
        row_vector_input = to_row_vector(np.asarray(init_array, dtype=float))
        norm = np.linalg.norm(row_vector_input)
        row_vector_input = row_vector_input / norm
        # res = np.dot(row_vector_input, row_vector_input.transpose())
        # modifiers = res[0][0]

        self.weight_matrix_input_hidden = np.dot(column_vector_hidden, row_vector_input)
        # self.weight_matrix_input_hidden = self.weight_matrix_input_hidden / modifiers


class SimpleFNN(NeuralNetwork):
    """
    单隐藏层前馈神经网络
    有激活函数
    """

    def __init__(self, input_nodes=1, output_nodes=1, hidden_nodes=1, learning_rate=0.3, feature_range=(0.01, 0.99)):
        super().__init__(input_nodes=input_nodes, output_nodes=output_nodes, learning_rate=learning_rate,
                         feature_range=feature_range)
        # 隐藏层节点数
        self.h_nodes = hidden_nodes

        # 权重矩阵随机生成
        self.weight_matrix_hidden_output = None
        self.weight_matrix_input_hidden = None
        self.init_weight_matrix2()

        # 激活函数
        self.activation_function = lambda x: expit(x)
        self.inverse_activation_function = lambda x: logit(x)

    def init_label_out(self):
        label_out = np.eye(self.o_nodes)
        label_out = minmax_scale(label_out, feature_range=self.feature_range)
        self.label_out = label_out

    def init_weight_matrix(self):
        """
        经过一些实践就会发现初始权重矩阵有一些小技巧和注意事项，然后总的来说不太重要，因此不需要精确
        """
        self.weight_matrix_input_hidden = np.random.rand(self.h_nodes, self.i_nodes) - 0.5
        self.weight_matrix_hidden_output = np.random.rand(self.o_nodes, self.h_nodes) - 0.5

    def init_weight_matrix2(self):
        """
        以0为中心的正态分布采样
        """
        self.weight_matrix_input_hidden = np.random.normal(
            0.0, pow(self.h_nodes, -0.5), (self.h_nodes, self.i_nodes))
        self.weight_matrix_hidden_output = np.random.normal(
            0.0, pow(self.o_nodes, -0.5), (self.o_nodes, self.h_nodes))

    def query(self, input_array):
        input_array = self.preprocessing_minmax_scale(input_array)

        hidden_input = np.dot(self.weight_matrix_input_hidden, input_array)
        hidden_output = self.activation_function(hidden_input)

        final_inputs = np.dot(self.weight_matrix_hidden_output, hidden_output)
        final_outputs = self.activation_function(final_inputs)

        return final_outputs

    def back_query_label(self, label: str):
        index = self.label_list.index(label)
        final_outputs = to_column_vector(self.label_out[index])

        final_inputs = self.inverse_activation_function(final_outputs)

        hidden_outputs = np.dot(self.weight_matrix_hidden_output.transpose(), final_inputs)

        hidden_outputs = self.preprocessing_minmax_scale(hidden_outputs)

        hidden_inputs = self.inverse_activation_function(hidden_outputs)

        inputs = np.dot(self.weight_matrix_input_hidden.transpose(), hidden_inputs)
        inputs = self.preprocessing_minmax_scale(inputs)

        inputs = inputs.reshape(-1)
        return inputs

    def query_label(self, input_array):
        final_outputs = self.query(input_array)
        index = np.argmax(final_outputs)
        return self.label_list[index]

    def train(self, input_array, label: str):
        input_array = self.preprocessing_minmax_scale(input_array)

        hidden_input = np.dot(self.weight_matrix_input_hidden, input_array)
        hidden_output = self.activation_function(hidden_input)

        final_inputs = np.dot(self.weight_matrix_hidden_output, hidden_output)
        final_outputs = self.activation_function(final_inputs)

        target_label_out = self.get_label_out(label)
        error_output = target_label_out - final_outputs

        error_hidden = np.dot(self.weight_matrix_hidden_output.transpose(), error_output)

        self.weight_matrix_hidden_output += self.lr * np.dot(
            to_column_vector(error_output * final_outputs * (1 - final_outputs)),
            to_row_vector(hidden_output))

        self.weight_matrix_input_hidden += self.lr * np.dot(
            to_column_vector(error_hidden * hidden_output * (1 - hidden_output)), to_row_vector(input_array))


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.INFO)


    def train_simple_fnn():
        epochs = 3
        learning_rate = 0.01

        nn = SimpleFNN(input_nodes=28 * 28, output_nodes=10, hidden_nodes=100, learning_rate=learning_rate)
        label_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        nn.set_label_list(label_list)

        train_data = load_mnist_train_data()

        for e in range(epochs):
            for label, value in train_data:
                label = str(label)
                nn.train(value, label)

            print(f'epoch {e} finished....')

        from pywander.models import save_model

        save_model(nn, 'mnist', 'simple_fnn.pkl')


    def test_simple_fnn():
        test_data = load_mnist_test_data()

        from pywander.models import load_model
        nn = load_model('mnist', 'simple_fnn.pkl')

        score_card = []
        for label, value in test_data:
            label = str(label)
            result_label = nn.query_label(value)

            if label == result_label:
                score_card.append(1)
            else:
                score_card.append(0)

        score_card = np.asarray(score_card)
        print(score_card.sum() / score_card.size)
        print('################################################')


    train_simple_fnn()
    test_simple_fnn()
