# gx-toolkit

`gx-toolkit`，全称为**Gx Company Development Toolkit** ，是**共享公司**专为智能开发、数据处理和AI打造的轻量级工具包。

## 如何安装

`gx-toolkit`目前有两个版本，分为**正式版**和**测试版**。

- **正式版**：发布在**PyPI**的版本，较为稳定
- **测试版**：发布在**TestPyPI**的版本，更新快

测试版在导入时需注意输入正确的**URL**：https://test.pypi.org/simple/

**正式版**安装方式：

```
pip install gxkit
```

**测试版**安装方式：

```
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.tuna.tsinghua.edu.cn/simple gxkit==0.1.0
```

**TestPyPI**上部分库**代码不全或没有最新版**，没有编译好的`.whl`文件（**PyPI**则不会有此问题），因此有部分依赖冲突。需要增加`extra-index-url`帮助用户获取最新版依赖库。

## 功能模块

- `dbtools` 通用数据库功能

## 快速入门

作者暂时懒得编写。请直接联系作者（shaojy@sunburst.com.cn）。

## 版本与许可证

当前的最新版本：`0.1.0`

许可证： `Apache License 2.0` 