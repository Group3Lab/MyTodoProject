# -*- coding: utf-8 -*-
"""
异常处理（try / except）学习示例
=================================

本文件把 Python 里和 try 相关的语法一次性讲全，每一步都给出可运行代码，
并尽量和 C / C++ 的写法对照，方便理解"为什么 Python 要这么设计"。

核心四个关键字（面试常考执行顺序）：
    try     ：圈出"可能出事"的代码
    except  ：出事之后怎么办（可以有多个，按顺序匹配）
    else    ：没出事时额外做什么（可选）
    finally ：不管出没出事，最后都要做什么（可选）

一句话记忆：
    try 里放可能出错的代码；except 抓错；else 是"没抓到才走"；finally 是"一定走"。
"""


# ============================================================
# 第 0 步：为什么需要 try？
# ============================================================
# 先看 C 的做法：函数返回一个错误码，调用方必须"记得"检查。
#
#     FILE* f = fopen("a.txt", "r");
#     if (f == NULL) {           // 忘了写这句？程序后面就崩了
#         perror("open failed");
#         return -1;
#     }
#
# 问题：错误码是"约定"，编译器不管你检不检查。忘了检查就是未定义行为。
#
# Python 的做法：出错就"抛异常"，会沿着调用栈自动往上传播，
# 直到有人接住它；如果一直没人接，程序才终止并打印堆栈。
#
# 关键区别（重点）：
#     C      ：错误是"返回值"，必须在每一层手动传递和检查
#     Python ：错误是"控制流"，会自动向上传播，你不接它才崩
#
# 所以 try 不是"可有可无的装饰"，它是 Python 处理错误的**正常机制**。


# ============================================================
# 第 1 步：最基础的 try / except
# ============================================================
# 语法：
#     try:
#         可能出错的代码
#     except 异常类型:
#         出错了做什么

print("=== 第 1 步：最基础的 try/except ===")

try:
    n = int("123")          # 正常，不抛
    print("转换成功:", n)
except ValueError:
    print("转换失败")

try:
    n = int("abc")          # 抛 ValueError
    print("这行不会执行")
except ValueError:
    print("抓到了 ValueError，程序继续往下走")
print()


# ============================================================
# 第 2 步：捕获指定类型 vs 不指定类型
# ============================================================
# except 后面可以写异常类型，也可以什么都不写。

# (1) 指定类型：只抓这一种（以及它的子类），其它异常照样往上抛。
#     下面故意用"错误"的类型演示抓不住的情况——外面必须再包一层才不会中断整个脚本。
try:
    try:
        x = 1 / 0
    except ValueError:          # 类型不对，抓不住 ZeroDivisionError
        print("不会执行")
except ZeroDivisionError:
    print("(1) 类型不匹配时，异常会穿过这个 except -> 被外层抓住（说明 except 不是万能兜底）")

try:
    x = 1 / 0
except ZeroDivisionError:
    print("(1) 指定类型 ZeroDivisionError：抓到了")

# (2) 不写类型（裸 except）：抓**所有**异常。
#     危害见第 12 步，这里只演示语法。
try:
    x = 1 / 0
except:
    print("(2) 裸 except：也抓到了（但不推荐，见第 12 步）")

# (3) 一条 except 抓多种类型：用元组
try:
    d = {"a": 1}
    v = d["b"]              # KeyError
except (KeyError, IndexError, ValueError):
    print("(3) 元组捕获：抓到了 KeyError")

# (4) 多个 except 分支：从上往下匹配，匹配到一个就跳过其余
try:
    int("abc")
except ZeroDivisionError:
    print("分支1")
except ValueError:
    print("(4) 多分支：命中分支2 ValueError")
except Exception:
    print("分支3")
print()


# ============================================================
# 第 3 步：as e —— 拿到异常对象
# ============================================================
# "except 类型 as 变量" 可以把异常对象绑定到一个名字上，方便打印或判断。
#
# 异常对象的常用属性 / 方法：
#     e.args     ：构造异常时传的参数，是一个元组
#     str(e)     ：给人看的错误信息（多数情况等于 e.args[0]）
#     repr(e)    ：给调试看的，含类型名
#     type(e)    ：异常的类型（类对象）
#     e.__traceback__ ：回溯信息（一般不用手动碰）
#
# 注意：as 绑定的变量在 except 块结束后**会被自动删除**（Python 3 的行为），
#       这是为了打断"异常对象 -> traceback -> 局部变量"的循环引用，帮助回收内存。

print("=== 第 3 步：as e 与异常对象 ===")

try:
    int("abc")
except ValueError as e:
    print("类型:", type(e).__name__)
    print("str(e):", str(e))
    print("repr(e):", repr(e))
    print("e.args:", e.args)
    print("isinstance(e, ValueError):", isinstance(e, ValueError))
    print("isinstance(e, Exception):", isinstance(e, Exception))
print()


# ============================================================
# 第 4 步：else —— 没抛异常时才执行
# ============================================================
# 语法：
#     try:    ...
#     except: ...
#     else:   ...      # 只有 try 里**没有**抛异常才执行
#
# 为什么要用 else，而不是把代码直接写在 try 里？
#     因为写在 try 里的代码如果抛异常，会被 except 一起抓走，
#     而你往往只想抓"那一步"的异常。放 else 里能精确区分：
#     "try 里的关键操作" 和 "成功之后才做的事"。

print("=== 第 4 步：else ===")

try:
    value = int("42")
except ValueError:
    print("转换失败")
else:
    # 只有转换成功才会走到这里，且这里的异常不会被上面的 except 吞掉
    print("else 分支：转换成功，值是", value * 2)
print()


# ============================================================
# 第 5 步：finally —— 无论如何都执行
# ============================================================
# finally 里的代码，无论 try 里是正常结束、抛异常、还是被 return/break 打断，
# **都会执行**。典型用途：关文件、释放锁、断开连接。
#
# C++ 对比：
#     finally ≈ RAII / 析构函数 / __try-__finally（SEH）
#     用途一样都是"保证清理一定发生"，只是 Python 写在语法层面。

print("=== 第 5 步：finally ===")

# (1) 出异常时 finally 照样执行
try:
    print("try: 准备出门")
    raise RuntimeError("出门前发现钥匙没带")
except RuntimeError as e:
    print("except:", e)
finally:
    print("finally: 无论如何都把门锁上")

# (2) 即使 return，finally 也会先执行（重点，容易被面试问）
def f():
    try:
        print("  f: try 里 return")
        return "try 的返回值"
    finally:
        print("  f: finally 仍然执行了！")

print("调用 f() 得到:", f())

# (3) 小心：finally 里的 return 会**覆盖** try 里的 return（坑，见第 19 步）
def g():
    try:
        return "try"
    finally:
        return "finally"     # 这个会赢

print("g() =", g(), "  <- 注意 finally 把 try 的返回值顶掉了")
print()


# ============================================================
# 第 6 步：完整四件套的执行顺序
# ============================================================
# 这是最常考的一条，务必背下来：
#
#   正常情况：try 全部 -> else -> finally
#   出错情况：try 中途 -> except -> finally        （else 不执行）
#   出错且没接住：try 中途 -> finally -> 继续往外抛
#
# 记忆：else 和 except 是"互斥"的两条路，finally 永远在最后。

print("=== 第 6 步：完整四件套执行顺序 ===")

def order(should_fail: bool):
    steps = []
    try:
        steps.append("try")
        if should_fail:
            raise ValueError("故意出错")
    except ValueError:
        steps.append("except")
    else:
        steps.append("else")
    finally:
        steps.append("finally")
    return steps

print("不失败:", order(False))    # ['try', 'else', 'finally']
print("失败  :", order(True))     # ['try', 'except', 'finally']
print()


# ============================================================
# 第 7 步：raise —— 主动抛出异常
# ============================================================
# 三种用法：
#     1) raise 异常类(...)        ：抛一个新的
#     2) raise 异常类              ：等价于 raise 异常类()，很少用
#     3) raise  （光秃秃一个）      ：把"当前正在处理的异常"原样再抛出去（re-raise）
#
# C++ 对比：throw 语句。语义几乎一样。

print("=== 第 7 步：raise ===")

def check_age(age: int):
    if age < 0:
        raise ValueError(f"年龄不能为负，收到 {age}")   # 主动抛
    return age

try:
    check_age(-1)
except ValueError as e:
    print("抓到主动抛出的:", e)

# re-raise：在 except 里用裸 raise 把原异常继续往上抛（常用于"记个日志再放行"）
def re_raise_demo():
    try:
        int("abc")
    except ValueError:
        print("  这里做了记录，然后原样再抛出去")
        raise                      # 裸 raise，保留原始 traceback

try:
    re_raise_demo()
except ValueError as e:
    print("上层再次抓到:", e)
print()


# ============================================================
# 第 8 步：raise ... from ... —— 异常链
# ============================================================
# 当"处理 A 异常时又抛出了 B 异常"，Python 会自动记录这种因果关系。
#
#     e.__context__ ：隐式链，"我在处理这个异常时又抛了新的"（自动记录）
#     e.__cause__   ：显式链，"这个新异常是由那个引起的"（用 from 指定）
#
# 语法：
#     raise 新异常 from 原异常      # 显式指定 cause
#     raise 新异常 from None        # 故意切断链，不显示原始异常
#     raise 新异常                  # 自动带 context

print("=== 第 8 步：异常链 from ===")

# (1) 隐式链：__context__ 被自动填上
try:
    try:
        int("abc")
    except ValueError:
        raise RuntimeError("包一层新的错误")
except RuntimeError as e:
    print("隐式链 context:", type(e.__context__).__name__)   # ValueError
    print("隐式链 cause  :", e.__cause__)                     # None

# (2) 显式链：用 from 指定 __cause__
def load_config(text: str):
    try:
        return int(text)
    except ValueError as e:
        raise RuntimeError("配置格式不合法") from e            # 明确"由它引起"

try:
    load_config("abc")
except RuntimeError as e:
    print("显式链 cause:", type(e.__cause__).__name__)        # ValueError
    print("错误信息      :", e)

# (3) 用 from None 切断链，不让底层细节暴露给用户
def friendly(text: str):
    try:
        return int(text)
    except ValueError as e:
        raise ValueError("请输入数字") from None

try:
    friendly("abc")
except ValueError as e:
    print("切断后 cause:", e.__cause__, "(None 表示已切断)")
print()


# ============================================================
# 第 9 步：自定义异常类
# ============================================================
# 自定义异常一律继承 Exception（不要继承 BaseException，见第 13 步）。
#
# 惯例：
#     - 类名以 Error 结尾
#     - 一个模块/项目先定义一个基类，便于统一捕获
#     - 需要额外信息就在 __init__ 里存下来
#
# C++ 对比：class MyError : public std::exception { ... };

print("=== 第 9 步：自定义异常 ===")

class AppError(Exception):
    """本项目所有业务异常的基类"""
    pass

class ValidationError(AppError):
    """校验失败"""
    def __init__(self, field: str, reason: str):
        self.field = field
        self.reason = reason
        # 记得调用父类构造，让 str(e) 有意义
        super().__init__(f"{field} 校验失败：{reason}")

def validate(age: int):
    if age < 0:
        raise ValidationError("age", "不能为负数")
    if age > 200:
        raise ValidationError("age", "不合常理")

# 可以精确抓子类
try:
    validate(-1)
except ValidationError as e:
    print(f"字段={e.field} 原因={e.reason}")
    print("str(e) =", e)

# 也可以抓统一基类，一次处理所有业务异常
try:
    validate(999)
except AppError as e:
    print("按基类捕获:", e)
print()


# ============================================================
# 第 10 步：异常层级与捕获顺序
# ============================================================
# 所有内置异常的根是 BaseException，下面是 Exception，再往下分各种子类。
#
# 重要规则：except 从上往下匹配，**匹配到第一个就停**。
#           所以子类必须写在父类前面，否则子类分支永远不会被命中。
#
#     except Exception:      # 父类
#         ...
#     except ValueError:     # 永远轮不到它！被上面的 Exception 吃掉了（死代码）
#         ...
#
# 关系链举例：
#     ValueError  -> Exception -> BaseException
#     IndexError  -> LookupError -> Exception

print("=== 第 10 步：捕获顺序 ===")

print("ValueError 是 Exception 的子类吗？", issubclass(ValueError, Exception))
print("KeyError   是 LookupError 的子类吗？", issubclass(KeyError, LookupError))

# 正确顺序：具体的在前，宽泛的在后
def classify(exc: Exception) -> str:
    try:
        raise exc
    except IndexError:              # 最具体
        return "IndexError 分支"
    except LookupError:             # 比 IndexError 宽，比 Exception 窄
        return "LookupError 分支"
    except Exception:               # 兜底，放最后
        return "Exception 兜底分支"

print(classify(IndexError()))       # 命中第一个
print(classify(KeyError()))         # 命中第二个
print(classify(ValueError()))       # 命中兜底
print()


# ============================================================
# 第 11 步：内置异常速查表
# ============================================================
# 常见的内置异常及触发场景（写代码时最常遇到的那些）：
#
#   ValueError          : 类型对但值不对，如 int("abc")
#   TypeError           : 类型用错，如 len(123)、1 + "a"
#   KeyError            : 字典键不存在，d["不存在"]
#   IndexError          : 序列下标越界，[1,2][5]
#   ZeroDivisionError   : 除以零，1/0、1%0
#   AttributeError      : 对象没有这个属性，None.xxx
#   NameError           : 用了没定义的变量
#   FileNotFoundError   : 打开不存在的文件（OSError 的子类）
#   PermissionError     : 没权限（OSError 的子类）
#   NotImplementedError : 抽象方法没实现（本项目 Menu.execute 抽象方法里就是这个）
#   KeyboardInterrupt   : 用户按 Ctrl+C（**不是** Exception 的子类！见第 13 步）
#   StopIteration       : 迭代器耗尽
#   OverflowError       : 数值运算溢出
#   RecursionError      : 递归太深
#
# 层级速记：
#   BaseException
#    ├── SystemExit
#    ├── KeyboardInterrupt
#    ├── GeneratorExit
#    └── Exception          ← 你写的业务代码基本都在这条线以下
#         ├── ValueError, TypeError, KeyError(LookupError), IndexError(LookupError)
#         ├── AttributeError, NameError, ZeroDivisionError, ArithmeticError
#         └── OSError ├── FileNotFoundError
#                     ├── PermissionError
#                     └── ...

print("=== 第 11 步：内置异常速查 ===")

for exc, thunk in [
    ("ValueError", lambda: int("abc")),
    ("TypeError", lambda: len(123)),
    ("KeyError", lambda: {"a": 1}["b"]),
    ("IndexError", lambda: [1, 2][5]),
    ("ZeroDivisionError", lambda: 1 / 0),
    ("AttributeError", lambda: None.whatever),
]:
    try:
        thunk()
    except Exception as e:
        print(f"  {exc:20s} -> 实际类型 {type(e).__name__}")
print()


# ============================================================
# 第 12 步：裸 except 的危害
# ============================================================
# "except:" 不带类型 = 抓所有异常，包括你根本处理不了的那些。
#
# 危害：
#     1) 掩盖真正的 bug：拼写错误、逻辑错误都会被当成"意料之中的错误"吞掉
#     2) 会连 KeyboardInterrupt（Ctrl+C）一起抓，用户按 Ctrl+C 退不出去
#     3) 出问题时没有任何信息，排查困难
#
# 正确做法：
#     - 尽量写具体的异常类型
#     - 确实要兜底，写 except Exception（**不是**裸 except），并把错误信息记下来
#
# 反例 vs 正例（下面真的执行一下，看差别）

print("=== 第 12 步：裸 except 的危害 ===")

def bad_divide(a, b):
    try:
        return a / b
    except:                 # 反例：什么都抓
        return None         # 调用方根本不知道是除零还是别的问题

def good_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError as e:      # 正例：明确知道在防什么
        print("  除数为 0，已处理:", e)
        return None

print("bad_divide(1, 0)  ->", bad_divide(1, 0))
print("good_divide(1, 0) ->", good_divide(1, 0))

# 裸 except 的经典事故：把"变量名打错"这种 bug 也吞了
def swallow_bug():
    try:
        total = 10
        print(total_valeu)      # 拼错了！本应 NameError 暴露出来
    except:
        pass                    # 结果被静默吞掉，你以为程序是好的

swallow_bug()
print("  swallow_bug() 悄悄失败，什么提示都没有 <- 这就是裸 except 的可怕之处")
print()


# ============================================================
# 第 13 步：BaseException vs Exception（重要）
# ============================================================
# except Exception 抓不到 KeyboardInterrupt / SystemExit / GeneratorExit，
# 因为它们直接继承 BaseException，不继承 Exception。这是**故意的设计**：
#
#     - KeyboardInterrupt（Ctrl+C）应该能中断程序
#     - SystemExit（sys.exit()）应该能正常退出
#
# 如果你写 except BaseException，就等于把这些"正常退出信号"也抓了，
# 用户按 Ctrl+C 会被你的代码吞掉，程序变得退不出去。
#
# 结论：
#     业务代码永远抓 Exception，不要抓 BaseException；
#     只有在写"最外层兜底/框架"时才可能考虑 BaseException，且必须 re-raise。

print("=== 第 13 步：BaseException vs Exception ===")
print("issubclass(KeyboardInterrupt, Exception) :", issubclass(KeyboardInterrupt, Exception))
print("issubclass(KeyboardInterrupt, BaseException):", issubclass(KeyboardInterrupt, BaseException))
print("issubclass(SystemExit, Exception)        :", issubclass(SystemExit, Exception))

# 这解释了为什么本项目 main.py 里要**专门**写一个 except KeyboardInterrupt：
# 因为 except Exception 抓不到它！
def demo_except_exception_does_not_catch_ctrl_c():
    try:
        # 用 SystemExit 模拟一个"非 Exception 的退出信号"
        raise SystemExit("模拟退出信号")
    except Exception:
        print("  这段不会执行 —— 因为 SystemExit 不是 Exception 的子类")
    except BaseException as e:
        print("  只能被 BaseException 抓到:", type(e).__name__)
        # 注意：抓到之后一般要 re-raise，否则会破坏正常的退出流程

demo_except_exception_does_not_catch_ctrl_c()
print()


# ============================================================
# 第 14 步：异常在函数调用栈中如何传播
# ============================================================
# 异常会沿着"调用栈"自动往上找 except，中间的函数不需要写任何检查代码。
# 这就是 Python 相对 C 返回码的最大优势：**不用每一层都传错误码**。
#
#     f3() 抛异常 -> f2() 没接住 -> f1() 没接住 -> 顶层接住
#
# 任何一层接住了，就不再继续往上走。

print("=== 第 14 步：跨层传播 ===")

def layer3():
    raise ValueError("来自最里层")

def layer2():
    layer3()        # 不处理，自动往上抛

def layer1():
    try:
        layer2()
    except ValueError as e:
        print("  在最外层接住:", e)

layer1()
print()


# ============================================================
# 第 15 步：with 与 try/finally 的关系
# ============================================================
# with 语句本质上就是 try/finally 的语法糖，用来自动做"清理"。
#
#     with 资源 as r:
#         ...使用 r...
#
# 等价于：
#     r = 资源.__enter__()
#     try:
#         ...使用 r...
#     finally:
#         r.__exit__(None, None, None)     # 一定执行清理
#
# 所以凡是"打开-使用-必须关闭"的场景（文件、锁、网络连接），优先用 with，
# 比手写 try/finally 更短、更不容易漏。

print("=== 第 15 步：with 与 try/finally ===")

# 手写 try/finally 版本
f = open("_trylearn_demo.txt", "w", encoding="utf-8")
try:
    f.write("用 try/finally 写文件\n")
finally:
    f.close()               # 保证一定关闭
print("try/finally 版本：文件已关闭")

# with 版本（等价，但更简洁）
with open("_trylearn_demo.txt", "a", encoding="utf-8") as f:
    f.write("用 with 追加一行\n")
# 出了 with 块文件自动关闭，不需要手写 close()
print("with 版本：文件已自动关闭")


# ============================================================
# 第 16 步：assert 与异常
# ============================================================
# assert 是"调试期"的检查，失败时抛 AssertionError。
#
#     assert 条件, "失败信息"
#
# 关键点：
#     1) 用 python -O 运行时，所有 assert 会被**整体移除**，所以绝不能用它做业务校验
#     2) 业务上必须成立的检查，要用 if + raise
#     3) assert 适合"断言这里一定为真，否则就是程序逻辑出了问题"

print("=== 第 16 步：assert ===")

def sqrt_like(x: float) -> float:
    assert x >= 0, "sqrt_like 只接受非负数"     # 调试期检查
    return x ** 0.5

print("sqrt_like(9) =", sqrt_like(9))
try:
    sqrt_like(-1)
except AssertionError as e:
    print("assert 失败 ->", e)
print()


# ============================================================
# 第 17 步：常见错误写法（避坑清单）
# ============================================================
# 这些是真实项目里最容易踩的坑，逐条对照检查自己的代码。
#
# 坑 1：裸 except（见第 12 步）
#       except:  ->  改成 except Exception:
#
# 坑 2：finally 里的 return 会覆盖 try 的 return（见第 5 步）
#       ->  finally 里不要写 return / break / continue
#
# 坑 3：在 except 里 raise 新异常却忘了 from，丢失根因
#       ->  raise NewError(...) from 原异常
#
# 坑 4：except 里 pass 静默吞掉异常
#       ->  至少记录日志，或者根本不该抓
#
# 坑 5：把 try 包得太大，一行出错整块跳过，难以定位
#       ->  try 只包"那一步"可能出错的代码
#
# 坑 6：except Exception 之后又在里面 raise 同一个异常导致重复处理
#
# 坑 7：用异常做正常的流程控制（比如用 KeyError 判断键存在）
#       ->  用 d.get(k) / in 判断更清晰
#
# 坑 8：捕获了异常但 except 块里又出了新异常，掩盖了原始问题

print("=== 第 17 步：避坑演示 ===")

# 坑 7 的正反例
d = {"a": 1}

try:
    v = d["missing"]            # 反例：用异常判断键在不在
except KeyError:
    v = None
print("用异常判断:", v)

v = d.get("missing")            # 正例：直接用 get
print("用 get 判断:", v)
print()


# ============================================================
# 第 18 步：实战 —— 输入健壮性
# ============================================================
# 对应本项目 src/main.py 里的 toNum() / safe_input()。
# 目标：不管用户输入什么（字母、超大数字、直接回车、Ctrl+C），程序都不崩。
#
# 关键技术点：
#     1) 可能的转换操作单独包 try，只抓 ValueError / TypeError
#     2) 输入流结束（EOFError）和 Ctrl+C（KeyboardInterrupt）要分开处理
#        —— 注意 KeyboardInterrupt 不是 Exception 子类，必须单独写
#     3) 转换失败要返回一个明确的"失败值"，让调用方好判断

print("=== 第 18 步：实战（输入健壮性）===")

def to_num(s):
    """把字符串转成整数，失败返回 -1（本项目 main.py 的做法）"""
    try:
        return int(s)
    except (ValueError, TypeError):
        return -1

def safe_input(prompt):
    """安全读取输入：Ctrl+C 当空串，EOF 返回 None"""
    try:
        return input(prompt).strip()
    except KeyboardInterrupt:       # Ctrl+C 不是 Exception 子类，必须单独抓
        print()
        return ""
    except EOFError:                # 输入流结束（管道输入耗尽等）
        print()
        return None

# 用假数据模拟各种恶劣输入，验证不会崩
for raw in ["123", "  42 ", "abc", "", "999999999999999999999999", "3.14", "0x10"]:
    result = to_num(raw)
    ok = "成功" if result != -1 else "失败"
    print(f"  to_num({raw!r:32s}) = {result:6d}  ({ok})")
print()


# ============================================================
# 第 19 步：把 try 用对的一般原则（总结）
# ============================================================
# 1. 能预防的先预防：先 if 判断，再考虑 try。
#    比如 d.get(k) 而不是 try d[k] except KeyError。
#
# 2. try 范围尽量小：只包真正可能出错的那几行。
#
# 3. 抓具体的异常：不要裸 except，不要用 BaseException 兜业务错误。
#
# 4. 抓到就要处理：要么恢复，要么给用户提示，要么记录后 re-raise。
#    什么都不做的 except 是最危险的。
#
# 5. 清理逻辑放 finally（或更好：用 with）。
#
# 6. 包装异常用 from 保留根因，除非你确实想对用户隐藏细节。
#
# 7. finally 里别写 return/break/continue。


# ============================================================
# 第 20 步：综合示例 —— 一个健壮的"读数字"循环
# ============================================================
# 把前面的知识点串起来：范围校验 + 自定义异常 + finally 清理 + 异常链。
#
# 模拟一个"让用户输入 1~100 的整数"的函数，无论怎么乱输入都安全返回。

print("=== 第 20 步：综合示例 ===")

class RangeError(AppError):
    """超出允许范围"""
    pass

def parse_range(text: str, low: int, high: int) -> int:
    """把 text 解析为 [low, high] 范围内的整数。

    失败时抛 AppError（带异常链），而不是返回 -1，
    因为这是"可预期的业务错误"，交给调用方决定怎么提示。
    """
    try:
        value = int(text)
    except (ValueError, TypeError) as e:
        # 用 from 保留原始异常，方便排查
        raise ValidationError("input", "不是合法整数") from e

    if not (low <= value <= high):
        raise RangeError(f"数字必须在 {low}~{high} 之间，收到 {value}")

    return value

# 逐个测试各种输入
for raw in ["50", "0", "101", "abc"]:
    try:
        result = parse_range(raw, 1, 100)
    except ValidationError as e:
        print(f"  {raw!r:8s} -> 校验失败: {e}  (根因: {type(e.__cause__).__name__})")
    except RangeError as e:
        print(f"  {raw!r:8s} -> 范围错误: {e}")
    else:
        print(f"  {raw!r:8s} -> OK: {result}")
    finally:
        # 这里的 finally 只是演示：每轮都执行
        pass
print()

# 用假输入跑一遍完整的 safe_input 循环（避免真的卡住等输入）
def robust_input_loop(stream):
    """从给定输入流读数字，直到拿到合法值或输入结束"""
    for i, raw in enumerate(stream):
        try:
            value = parse_range(raw, 1, 100)
        except AppError as e:
            print(f"  第{i+1}次输入 {raw!r} 不合法：{e}")
            continue
        else:
            print(f"  第{i+1}次输入成功：{value}")
            return value
    print("  输入流结束，未获得合法值")
    return None

print("模拟一串乱输入：")
robust_input_loop(["abc", "999", "42"])
print()


# ============================================================
# 第 21 步：清理临时文件
# ============================================================
import os
if os.path.exists("_trylearn_demo.txt"):
    os.remove("_trylearn_demo.txt")


# ============================================================
# 总结：try 相关语法速查表
# ============================================================
# ┌────────────────────────────┬──────────────────────────────────────────────┐
# │ 语法                       │ 作用                                         │
# ├────────────────────────────┼──────────────────────────────────────────────┤
# │ try: ...                   │ 圈出可能出错的代码                           │
# │ except 类型: ...           │ 抓指定异常（可多个，按顺序匹配，子类在前）   │
# │ except (A, B): ...         │ 一条抓多种类型                               │
# │ except 类型 as e: ...      │ 绑定异常对象，用 e.args / str(e) 等          │
# │ except: ...                │ 裸捕获（不推荐，会吞掉 Ctrl+C 和 bug）        │
# │ except Exception: ...      │ 兜底业务异常（推荐写法）                     │
# │ else: ...                  │ try 没抛异常时才执行（与 except 互斥）       │
# │ finally: ...               │ 无论如何都执行（清理）；里面别写 return      │
# │ raise X(...)               │ 主动抛出新异常                               │
# │ raise                      │ 把当前异常原样再抛（re-raise）               │
# │ raise X from Y             │ 显式异常链，记下 __cause__                   │
# │ raise X from None          │ 切断异常链，隐藏底层细节                     │
# │ with ... as ...:           │ try/finally 的语法糖，自动清理               │
# │ assert 条件, 消息          │ 调试期断言（-O 下会被移除，别做业务校验）    │
# └────────────────────────────┴──────────────────────────────────────────────┘
#
# 执行顺序（背下来）：
#     成功：try -> else -> finally
#     失败：try -> except -> finally
#     没接住：try -> finally -> 继续往上抛
#
# 异常对象常用属性：
#     e.args          构造参数元组
#     str(e)          用户可读信息
#     type(e).__name__ 异常类型名
#     e.__cause__     显式链（raise ... from ...）
#     e.__context__   隐式链（处理异常时又抛新异常）
#
# 层级（简化）：
#     BaseException
#      ├── KeyboardInterrupt   <- except Exception 抓不到！
#      ├── SystemExit          <- 同上
#      └── Exception           <- 业务代码在这条线以下
#           ├── ValueError / TypeError / AttributeError / ZeroDivisionError
#           ├── LookupError ├── KeyError
#           │               └── IndexError
#           └── OSError ├── FileNotFoundError
#                       └── PermissionError
