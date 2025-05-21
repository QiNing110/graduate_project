import json

def fix_json_file(input_file, output_file):
    try:
        # 读取文件内容
        with open(input_file, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 替换错误的']['为','
        fixed_content = content.replace('][', ',')
        
        # 尝试解析修复后的内容，验证是否为有效的JSON
        try:
            json.loads(fixed_content)
            print("修复后的内容是有效的JSON格式")
        except json.JSONDecodeError as e:
            print(f"修复后的内容仍然不是有效的JSON格式: {e}")
            # 即使验证失败，仍然保存修复后的内容
            print("但仍将修复后的内容保存到输出文件")
        
        # 保存修复后的内容到新文件
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(fixed_content)
        
        print(f"已成功修复并保存到 {output_file}")
        return True
        
    except FileNotFoundError:
        print(f"错误: 文件 {input_file} 未找到")
        return False
    except Exception as e:
        print(f"错误: 发生了一个未知错误: {e}")
        return False

if __name__ == "__main__":
    input_file = 'GraphRAG_SFT_LLM_eval_results.json'  # 请替换为实际的输入文件路径
    output_file = 'GraphRAG_SFT_LLM_eval_results.json'  # 请替换为实际的输出文件路径
    
    fix_json_file(input_file, output_file)    