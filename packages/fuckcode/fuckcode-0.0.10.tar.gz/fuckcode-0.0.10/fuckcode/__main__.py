"""
入口文件
"""
import typer
from . import translate as t
import subprocess

app = typer.Typer()

    
@app.command()
def translate(fc_code: str, o: str = typer.Option(..., "--output", "-o")):
    """
    翻译 FuckCode 到 C++
    """
    #读取 fc_code
    with open(fc_code, "r", encoding="utf-8") as f:
        fc_code_text = f.read()
    cpp_code = t.translate_fc_to_cpp(fc_code_text)
    with open(o, "w", encoding="utf-8") as f:
        f.write(cpp_code)
    typer.echo(f"已保存到 {o}")

@app.command()
def compiler(fc_code: str, o: str = typer.Option(..., "--output", "-o")):
    """
    通过 g++ 编译 FuckCode
    """
    with open(fc_code, "r", encoding="utf-8") as f:
        fc_code_text = f.read()
    cpp_code = t.translate_fc_to_cpp(fc_code_text)
    with open(fc_code+".cpp", "w", encoding="utf-8") as f:
        f.write(cpp_code)
    typer.echo("正在编译...")
    r = subprocess.run(["g++", fc_code+".cpp", "-o", o])
    if r.returncode != 0:
         typer.echo("编译失败")
    else:
        typer.echo(f"已编译到 {o}")


def main():
    """
    主函数
    """
    app()

if __name__ == "__main__":
    main()