# NFT Generator

# 使用方法

## 素材准备

* 所有图层的尺寸需要一样，但并不一定要是正方形
* 支持的格式/拓展名： png, gif, jpg, jpeg, tif, tiff, webp
* 文件夹结构需要按照下面的示例进行整理，即按照图层顺序自顶向下进行编号，文件夹格式一定是 `<数字>.<图层名>` 的格式，`点` 两边不要有空格

```Plaintext
|-- SomeNFT
    |-- 1.嘴        // 最上面的图层
    |-- 2.眼睛
    |-- 3.脸
    |-- 4.头
    |-- 5.衣服
    |-- 6.背景      // 最下面的图层
```

## 操作步骤

### 第一步：生成藏品（与 Excel、元数据）

1. 双击 `NFT-Generator.exe`（Windows）或者 `NFT-Generator.app`（macOS）启动软件，等待初始化。启动图像处理服务耗时略长，需要等待大约十秒钟的时间。启动完毕后提示语会消失，带有开始按钮的主界面会显示。（注：您会看到有两个窗口被打开了，可以忽略其中名为 `Developer Tools` 的窗口。）
2. 填写必要的信息
   1. 点击 `素材文件夹` 右侧的 `浏览…` 按钮打开文件夹选择对话框，选择素材所在的文件夹。在上述示例中，就是 `SomeNFT` 文件夹。
   2. `输出文件夹` 会自动填入，即默认将输出文件写入素材文件夹内的 `output` 文件夹，但您依然可以点击右侧的 `浏览…` 按钮选择其他文件夹。
   3. 输入 `素材大小`，以像素为单位，默认图像是正方形。
   4. 输入 `藏品系列名称`，该信息会被写入到元数据中。
   5. 输入 `生成藏品数量`
   6. 输入 `起始编号`，藏品将从该数字开始编号。
   7. 按需打开 `输出元数据（JSON）` 开关，并选择 `Metadata 标准`，本软件支持生成 JSON 格式的 metadata。（注：ERC721 和 ERC1155 标准中都包含了获取 metadata URI 的功能，一些 Dapp 会通过这个方式检索 NFT 的基本信息，比如 ConfluxScan 或者钱包等）。
3. 点击 `开始` 按钮即开始生成，您可以通过进度条关注执行状况。

### 第二步：生成元数据

__藏品筛选__
`2.0.0` 版本之后会强制生成一个 Excel 文件，内有上述步骤生成的所有藏品的图层信息。您可以根据需求剔除部分藏品，只需要将表格中第二列（即 `是否选中` 列）中的“是”改成“否”即可。

1. 点击上方按钮切换至 `第二步：生成元数据`
2. 填写必要信息
   1. 点击 `Excel 文件` 右侧的 `浏览…` 按钮打开文件选择对话框，选择 `第一步所生成的 Excel 文件`，要求和所生成的藏品图片放在同一个文件夹中（如果您没有移动文件的话，它们默认就是在一起的）。`输出文件夹` 会被强制设定为 Excel 文件所在的文件夹，生成的元数据会放在 `metadata` 子文件夹中（自动创建）。
   2. 输入 `藏品系列名称`，同第一步。
   3. `清理不需要的图片` 默认处于开启状态，会根据 Excel 中的信息将那些标记为未被选中的文件删除，删除的文件会放在回收站（Windows）或者废纸篓（macOS）中。
   4. `重新排序图片` 默认处于开启状态，如果 Excel 中存在未被选中的藏品，则部分文件的编号会变得不连续，该功能会重新进行编号。重排时以 Excel 中第一个藏品的编号作为起始编号。
   5. 选择 `Metadata 标准`，同第一步。
3. 点击 `开始` 按钮即开始生成。

## 问题反馈

如果您遇上任何技术问题，请尽可能在第一时间给两个窗口截图并发送给我们。谢谢。