import torch

FEAT_SIZE = 10
BYTES_FOR_FLOAT32 = 4
BYTES_FOR_FLOAT16 = 2


def to_mb(size: int) -> float:
    return size / 1024 / 1024


class Float32ModelWithBias(torch.nn.Module):
    def __init__(self):
        super(Float32ModelWithBias, self).__init__()
        self.linear1 = torch.nn.Linear(
            FEAT_SIZE, FEAT_SIZE, bias=True, dtype=torch.float32
        )
        self.linear2 = torch.nn.Linear(
            FEAT_SIZE, FEAT_SIZE, bias=True, dtype=torch.float32
        )
        self.linear3 = torch.nn.Linear(
            FEAT_SIZE, FEAT_SIZE, bias=True, dtype=torch.float32
        )

    def forward(self, x):
        return self.linear3(self.linear2(self.linear1(x)))

    @property
    def layer_num(self):
        return 3

    @property
    def weight_size(self):
        return (FEAT_SIZE * FEAT_SIZE) * self.layer_num

    @property
    def bias_size(self):
        return FEAT_SIZE * self.layer_num

    @property
    def model_size(self):
        return (self.weight_size + self.bias_size) * BYTES_FOR_FLOAT32


class Float32ModelWithOutBias(torch.nn.Module):
    def __init__(self):
        super(Float32ModelWithOutBias, self).__init__()
        self.linear1 = torch.nn.Linear(
            FEAT_SIZE, FEAT_SIZE, bias=False, dtype=torch.float32
        )
        self.linear2 = torch.nn.Linear(
            FEAT_SIZE, FEAT_SIZE, bias=False, dtype=torch.float32
        )
        self.linear3 = torch.nn.Linear(
            FEAT_SIZE, FEAT_SIZE, bias=False, dtype=torch.float32
        )

    def forward(self, x):
        return self.linear3(self.linear2(self.linear1(x)))

    @property
    def layer_num(self):
        return 3

    @property
    def weight_size(self):
        return (FEAT_SIZE * FEAT_SIZE) * self.layer_num

    @property
    def bias_size(self):
        return 0 * self.layer_num

    @property
    def model_size(self):
        return (self.weight_size + self.bias_size) * BYTES_FOR_FLOAT32


class Float16ModelWithBias(torch.nn.Module):
    def __init__(self):
        super(Float16ModelWithBias, self).__init__()
        self.linear1 = torch.nn.Linear(
            FEAT_SIZE, FEAT_SIZE, bias=True, dtype=torch.float16
        )
        self.linear2 = torch.nn.Linear(
            FEAT_SIZE, FEAT_SIZE, bias=True, dtype=torch.float16
        )
        self.linear3 = torch.nn.Linear(
            FEAT_SIZE, FEAT_SIZE, bias=True, dtype=torch.float16
        )

    def forward(self, x):
        return self.linear3(self.linear2(self.linear1(x)))

    @property
    def layer_num(self):
        return 3

    @property
    def weight_size(self):
        return (FEAT_SIZE * FEAT_SIZE) * self.layer_num

    @property
    def bias_size(self):
        return FEAT_SIZE * self.layer_num

    @property
    def model_size(self):
        return (self.weight_size + self.bias_size) * BYTES_FOR_FLOAT16
