import os
import argparse
import subprocess
import sys
import glob
import time
from multiprocessing import Pool, cpu_count


def process_pdb_id(pdb_id, out_dir):
    """处理单个pdb id的转换和重命名逻辑（可被多进程调用）"""
    print(f"开始处理 {pdb_id} ...")
    
    # 构建输入文件路径
    input_cif = os.path.join(
        '/mnt/bn/ai4sml-lq/dev/alphafold3-data/wwPDB/pdb/mmcif/',
        f'{pdb_id}.cif'
    )

    # 检查输入文件是否存在
    if not os.path.exists(input_cif):
        print(f"警告：输入文件 {input_cif} 不存在，跳过该id", file=sys.stderr)
        return

    # 执行protenix命令
    cmd = [
        'protenix', 'tojson',
        '--input', input_cif,
        '--out_dir', out_dir
    ]

    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print(f"错误：处理 {pdb_id} 时命令执行失败\n错误信息：{e.stderr}", file=sys.stderr)
        return

    # 等待文件写入完成（避免重命名时文件未完全生成）
    time.sleep(0.1)

    # 查找生成的随机后缀文件
    generated_files = glob.glob(os.path.join(out_dir, f"{pdb_id}-*.json"))

    # 验证查找结果
    if not generated_files:
        print(f"警告：{pdb_id} 未生成JSON文件，跳过重命名", file=sys.stderr)
        return
    if len(generated_files) > 1:
        print(f"警告：{pdb_id} 生成多个文件 {generated_files}，仅重命名第一个", file=sys.stderr)

    # 目标文件名
    target_path = os.path.join(out_dir, f"{pdb_id}.json")

    # 重命名（若目标文件已存在则覆盖）
    try:
        os.rename(generated_files[0], target_path)
        print(f"成功处理 {pdb_id}：{os.path.basename(generated_files[0])} -> {os.path.basename(target_path)}")
    except Exception as e:
        print(f"错误：{pdb_id} 重命名失败，原因：{str(e)}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description='多进程批量转换PDB文件到固定命名的JSON格式')
    parser.add_argument('--out_dir', required=True, help='输出目录路径（必填）')
    parser.add_argument('--processes', type=int, default=cpu_count(), 
                       help=f'并行进程数（默认使用CPU核心数 {cpu_count()}）')
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    pdb_list_path = os.path.join(script_dir, 'recentpdb384.txt')

    if not os.path.exists(pdb_list_path):
        print(f"错误：未找到id列表文件 {pdb_list_path}", file=sys.stderr)
        sys.exit(1)

    with open(pdb_list_path, 'r') as f:
        pdb_ids = [line.strip() for line in f if line.strip()]

    os.makedirs(args.out_dir, exist_ok=True)

    # 创建进程池并并行处理
    with Pool(processes=args.processes) as pool:
        # 使用starmap传递多个参数（pdb_id和out_dir）
        pool.starmap(process_pdb_id, [(pdb_id, args.out_dir) for pdb_id in pdb_ids])

    print("所有任务处理完成")


if __name__ == '__main__':
    main()
