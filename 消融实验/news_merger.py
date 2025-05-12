import os
from pathlib import Path

def merge_news_files(source_dir, output_file):
    """合并新闻文件夹中所有txt文件到一个文件中"""
    # 创建输出文件
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # 定义六个分类
        categories = ['体育', '娱乐', '时尚', '社会', '科技', '财经']
        
        for category in categories:
            category_dir = os.path.join(source_dir, category)
            # 检查分类文件夹是否存在
            if not os.path.exists(category_dir):
                print(f"分类文件夹 '{category}' 不存在，跳过")
                continue
            
            # 写入分类标题
            outfile.write(f"{category}新闻\n\n")
            
            # 获取该分类下所有txt文件
            txt_files = [f for f in os.listdir(category_dir) 
                         if f.endswith('.txt') and os.path.isfile(os.path.join(category_dir, f))]
            
            # 处理每个txt文件
            for i, txt_file in enumerate(txt_files):
                file_path = os.path.join(category_dir, txt_file)
                try:
                    # 读取文件内容
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        content = infile.read().strip()
                        # 写入文件内容
                        outfile.write(f"{content}\n\n")
                    
                    # 写入分隔线（根据文件序号使用不同长度的分隔线，使视觉更清晰）
                    separator = '----------------------------------------------------------------------'
                    if i % 2 == 0:
                        separator = '---------------------------------------------------------'
                    outfile.write(f"{separator}\n\n")
                    
                except Exception as e:
                    print(f"处理文件 '{file_path}' 时出错: {str(e)}")
            
            # 写入分类分隔线
            outfile.write(f"{'=' * 40}\n\n")
    
    print(f"所有新闻文件已合并到 '{output_file}'")

if __name__ == "__main__":
    # 设置源文件夹路径（请根据实际情况修改）
    source_directory = "./dataset/news"
    # 设置输出文件路径
    output_file_path = "./dataset/news/合并新闻.txt"
    
    # 确保源文件夹存在
    if not os.path.exists(source_directory):
        print(f"错误：源文件夹 '{source_directory}' 不存在")
    else:
        merge_news_files(source_directory, output_file_path)    