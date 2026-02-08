import argparse
import os
import os.path as osp
import shutil
from tqdm import tqdm  # 如果没有安装 tqdm 可以去掉这行和下面的 tqdm 包装

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('data_path', help='ade20k data path')
    args = parser.parse_args()

    # 1. 锁定源目录：直接定位到 data/ade/ADE20K_2021_17_01
    # 如果用户改名了，脚本会自动尝试寻找
    base_path = args.data_path
    source_dir = None
    
    # 尝试寻找包含 images 的子目录
    potential_dirs = [
        osp.join(base_path, 'ADE20K_2021_17_01'),
        osp.join(base_path, 'ADEChallengeData2016'),
        base_path # 也许源文件就在当前目录
    ]
    
    for d in potential_dirs:
        if osp.exists(osp.join(d, 'images')):
            source_dir = d
            break
            
    if not source_dir:
        print(f"❌ 错误: 在 {base_path} 下没找到 'ADE20K_2021_17_01' 或 'ADEChallengeData2016'")
        return

    print(f"✅ 找到源数据目录: {source_dir}")

    # 2. 定义目标目录 (SegFormer 标准结构)
    # 目标是 data/ade/images 和 data/ade/annotations
    target_root = base_path 
    if source_dir == base_path: 
        # 防止源和目标重叠，如果用户直接传了内层目录，往上一层存
        target_root = osp.dirname(base_path)

    os.makedirs(osp.join(target_root, 'images', 'training'), exist_ok=True)
    os.makedirs(osp.join(target_root, 'images', 'validation'), exist_ok=True)
    os.makedirs(osp.join(target_root, 'annotations', 'training'), exist_ok=True)
    os.makedirs(osp.join(target_root, 'annotations', 'validation'), exist_ok=True)

    print(f"🚀 开始移动文件到: {target_root}")
    
    count = 0
    # 3. 遍历源目录
    for root, dirs, files in os.walk(source_dir):
        # 跳过我们新创建的目标目录 (防止死循环)
        # 只有当路径完全匹配目标目录时才跳过，而不是只要包含 'images' 就跳过
        if os.path.abspath(root).startswith(os.path.abspath(osp.join(target_root, 'images'))) or \
           os.path.abspath(root).startswith(os.path.abspath(osp.join(target_root, 'annotations'))):
            continue

        for filename in files:
            if filename.endswith('.jpg'):
                # 判断是训练集还是验证集
                if 'training' in root:
                    split = 'training'
                elif 'validation' in root:
                    split = 'validation'
                else:
                    continue

                basename = filename[:-4]
                src_img = osp.join(root, filename)
                src_mask = osp.join(root, basename + '_seg.png')

                # 只有成对才移动
                if osp.exists(src_mask):
                    # 移动图片 -> data/ade/images/training/xxx.jpg
                    dst_img = osp.join(target_root, 'images', split, filename)
                    shutil.move(src_img, dst_img)

                    # 移动标签 -> data/ade/annotations/training/xxx.png
                    dst_mask = osp.join(target_root, 'annotations', split, basename + '.png')
                    shutil.move(src_mask, dst_mask)
                    
                    count += 1
                    if count % 2000 == 0:
                        print(f"   已处理 {count} 张...")

    print(f"🎉 处理完成！共成功整理 {count} 对图片和标签。")
    print(f"现在数据位于: {target_root}/images 和 {target_root}/annotations")

if __name__ == '__main__':
    main()