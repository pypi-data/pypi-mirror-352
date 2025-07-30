# inkhinge

`inkhinge`是一个简单的Python包，提供基本的数学运算功能。通过`pip install inkhinge`安装后，你可以使用其中的函数进行数字运算。

## 安装
pip install inkhinge
## 使用方法

下面是一个简单的使用示例：
from inkhinge import add_numbers, multiply_numbers

# 加法运算
result = add_numbers(1, 2)
print(f"1 + 2 = {result}")  # 输出: 1 + 2 = 3

# 乘法运算
result = multiply_numbers(2, 3)
print(f"2 * 3 = {result}")  # 输出: 2 * 3 = 6
## 函数文档

### `add_numbers(a, b)`
将两个数字相加。

参数:
- `a`: 第一个数字
- `b`: 第二个数字

返回:
- 两个数字的和

### `multiply_numbers(a, b)`
将两个数字相乘。

参数:
- `a`: 第一个数字
- `b`: 第二个数字

返回:
- 两个数字的乘积

## 贡献

如果你想为`inkhinge`包做出贡献，请遵循以下步骤：

1. Fork这个仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 将更改推送到你的分支 (`git push origin feature/AmazingFeature`)
5. 打开一个Pull Request

## 许可证

本项目采用MIT许可证 - 详情请见[LICENSE](LICENSE)文件。    