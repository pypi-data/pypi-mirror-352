"""
英文原文行-中文翻译行

保留中文行，保留空白行，其余移除。
"""


from pywander.text.line import is_contain_chinese, is_blank_line


def remove_english_line(in_file, out_file, record_file):
    with open(in_file, 'rt', encoding='utf8') as f:
        with open(out_file, 'wt', encoding='utf8') as f_out:
            with open(record_file, 'wt', encoding='utf8') as f_record:
                for line in f:
                    if is_contain_chinese(line):
                        f_out.write(line)
                    elif is_blank_line(line):
                        f_out.write(line)
                    else:
                        f_record.write(line)