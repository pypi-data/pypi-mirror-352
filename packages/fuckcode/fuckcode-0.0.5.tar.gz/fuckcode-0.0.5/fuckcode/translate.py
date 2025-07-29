def translate_fc_to_cpp(fc_code: str) -> str:
    """将.fc代码转换为.cpp代码
    
    Args:
        fc_code: 输入的.fc格式代码字符串
        
    Returns:
        转换后的.cpp格式代码字符串
    """
    lines = fc_code.splitlines()
    cpp_lines = []
    indent_stack = []  # 缩进栈，记录函数/代码块起始缩进
    pending_braces = []  # 待闭合的花括号
    
    for line in lines:
        stripped = line.lstrip()
        if not stripped:  # 空行
            cpp_lines.append(line)
            continue
            
        current_indent = len(line) - len(stripped)
        
        # 处理待闭合的花括号
        while pending_braces and current_indent <= pending_braces[-1]:
            cpp_lines.append(' ' * pending_braces.pop() + '}')
            
        # 处理函数定义后的冒号
        if stripped.endswith(':'):
            cpp_lines.append(line.replace(':', ' {'))
            indent_stack.append(current_indent)
            pending_braces.append(current_indent)
            continue
            
        # 添加分号（排除预处理指令和注释）
        if not (stripped.startswith('#') or stripped.startswith('//')):
            if not stripped.endswith(';'):
                line = line.rstrip() + ';'
                
        cpp_lines.append(line)
    
    # 关闭所有未闭合的花括号
    while pending_braces:
        cpp_lines.append(' ' * pending_braces.pop() + '}')
    
    return '\n'.join(cpp_lines)

if __name__ == "__main__":
    # 示例用法
    with open('test.fc', 'r') as f:
        fc_code = f.read()
    cpp_code = translate_fc_to_cpp(fc_code)
    with open('test.cpp', 'w') as f:
        f.write(cpp_code)