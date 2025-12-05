import re


def remove_book_tags(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile:
        content = infile.read()

    # 使用正则表达式匹配并移除所有的 { ... |BOOK} 标签
    content = re.sub(r'\{([^\|\}]+)\|BOOK\}', r'\1', content)

    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write(content)


# 代码实现
def clean_txt_file(file_path):
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 处理内容：删除只有一个单词的行
    cleaned_lines = [line for line in lines if len(line.split()) > 1]

    # 保存回原文件
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(cleaned_lines)




if __name__ == "__main__":
    # input_file = './GuNER2023_train.txt'
    # output_file = './GuNER2023_train_cleaned.txt'
    # remove_book_tags(input_file, output_file)
    # print(f"All BOOK tags have been removed and saved to {output_file}")
    # 使用方法
    file_path = './BIO/val_bio.txt'  # 替换为你的txt文件路径
    clean_txt_file(file_path)