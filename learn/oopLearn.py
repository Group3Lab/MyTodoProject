# -*- coding: utf-8 -*-
"""
面向对象（OOP）学习示例
=========================

本文件从"结构体式写法"一路演进到"完整的面向对象写法"，
每一步都对应 C / C++ 里你会写的东西，方便对照理解。

核心四个概念：
    1. 封装（Encapsulation）：把数据和方法绑在一起，隐藏内部细节
    2. 继承（Inheritance）  ：子类复用父类的属性和方法
    3. 多态（Polymorphism） ：同一接口，不同表现
    4. 抽象（Abstraction）  ：只暴露"做什么"，不暴露"怎么做"
"""

from typing import List


# ============================================================
# 第 0 步：为什么需要类？
# ============================================================
# 在 C 里，描述一个"学生"你只能这样写：
#
#     struct Student {
#         char name[32];
#         int  age;
#         int  score;
#     };
#     struct Student stu = {"Tom", 18, 90};
#
# 数据和行为是分开的：你想打印姓名，要自己写一个函数，
# 还得手动把 stu 传进去：
#     void PrintStudent(struct Student* s) { ... }
#
# 在 Python 里，数据和行为可以打包进同一个"类"里，
# 对象自己知道该怎么做，这就是"封装"。


# ============================================================
# 第 1 步：最基础的类
# ============================================================
class Student:
    """学生类：一个最小的类示例。

    对应 C++ 里大概是：
        class Student {
        public:
            std::string name;
            int age;
            int score;
            void Print();
        };
    """

    # 类属性：所有实例共享，类似 C++ 的 static 成员
    # 注意：这里记录的是"全校人数"，属于整个类，不属于某个学生
    count: int = 0

    def __init__(self, name: str, age: int, score: int):
        """构造函数，对应 C++ 的 Student(...)。

        注意第一个参数必须是 self，相当于 C++ 里隐藏的 this 指针。
        Python 不会自动帮你声明成员变量，赋值即声明。
        """
        # 实例属性：每个对象各自一份
        self.name = name
        self.age = age
        self.score = score

        # 每创建一个对象，类属性 +1
        # 这里必须用 Student.count 而不是 self.count
        # 否则会"在实例上新建一个属性"，类属性反而不会变
        Student.count += 1

    def Print(self):
        """成员方法。调用时 stu.Print() 会自动把 stu 传给 self。"""
        print(f"姓名：{self.name:<8} 年龄：{self.age:<4} 分数：{self.score}")


print("=== 第 1 步：基础类 ===")
stu1 = Student("Tom", 18, 90)
stu2 = Student("Jerry", 19, 85)
stu1.Print()
stu2.Print()
print(f"当前学生总数：{Student.count}")     # 类属性用类名访问
print(f"学生总数（也可用实例访问）：{stu1.count}")
print()


# ============================================================
# 第 2 步：封装 —— 把数据藏起来，用方法去访问
# ============================================================
# 为什么需要封装？
# 因为直接改属性可能改出"非法状态"：
#     stu.age = -5      # 年龄变成负数，程序不会报错，但逻辑崩了
#
# C++ 用 private + getter/setter 解决；
# Python 没有真正的 private，靠"约定 + 语法糖"。

class BankAccount:
    """银行账户：演示 Python 的封装。

    Python 的三种"访问权限"约定（注意：都是约定，不是强制）：
        name    —— 公开，随便访问
        _name   —— 单下划线，protected 的含义："这是内部用的，你别碰"
        __name  —— 双下划线，会被"名字改写"，接近 private 的效果

    C++ 对比：
        public / protected / private 是编译器强制的；
        Python 全靠"程序员自觉"，所以叫"约定优于强制"。
    """

    # C++ 里的常量成员/静态常量，Python 一般写成全大写类属性
    __MIN_AMOUNT: int = 0       # 双下划线：外部拿不到

    def __init__(self, owner: str, balance: int = 0):
        self.__owner = owner        # 私有属性
        self.__balance = balance    # 私有属性
        self._history: List[str] = []   # 受保护属性（子类可用）

    # ---------- getter：只读访问 ----------
    @property
    def balance(self) -> int:
        """把方法"伪装"成属性：外部写 account.balance，不用写 account.balance()。

        这是 Python 特有的语法糖，C++ 里得写 int GetBalance() const。
        """
        return self.__balance

    @property
    def owner(self) -> str:
        return self.__owner

    # ---------- setter：带校验的写入 ----------
    @balance.setter
    def balance(self, value: int):
        """这样写以后，account.balance = -1 也会被拦截。

        @property + 同名 setter 的组合，等价于 C++ 的
        int GetBalance() / void SetBalance(int) 但用起来更自然。
        """
        if value < self.__MIN_AMOUNT:
            raise ValueError(f"余额不能为负数：{value}")
        self.__balance = value

    # ---------- 业务方法 ----------
    def Deposit(self, amount: int) -> bool:
        """存款。返回布尔值表示是否成功，调用方可以据此判断。"""
        if amount <= 0:
            print(f"存款失败：金额 {amount} 无效")
            return False
        self.__balance += amount
        self._history.append(f"存入 {amount}，余额 {self.__balance}")
        print(f"存款成功：{amount} 元，当前余额 {self.__balance} 元")
        return True

    def Withdraw(self, amount: int) -> bool:
        """取款。"""
        if amount <= 0:
            print(f"取款失败：金额 {amount} 无效")
            return False
        if amount > self.__balance:
            print(f"取款失败：余额 {self.__balance} 元不足以取出 {amount} 元")
            return False
        self.__balance -= amount
        self._history.append(f"取出 {amount}，余额 {self.__balance}")
        print(f"取款成功：{amount} 元，当前余额 {self.__balance} 元")
        return True

    # ---------- 魔术方法（dunder method）----------
    def __str__(self) -> str:
        """对应 C++ 的 operator<< 重载，print(对象) 时会调用它。"""
        return f"<BankAccount owner={self.__owner} balance={self.__balance}>"

    def __repr__(self) -> str:
        """在交互式环境/列表里显示时用，理想情况下应是"可重建对象的字符串"。"""
        return f"BankAccount('{self.__owner}', {self.__balance})"

    def __eq__(self, other) -> bool:
        """对应 C++ 的 operator== 。不重载的话，== 比较的是"是不是同一个对象"。"""
        if not isinstance(other, BankAccount):
            return NotImplemented
        return self.__owner == other.__owner and self.__balance == other.__balance


print("=== 第 2 步：封装 ===")
account = BankAccount("userA", 5000)
print(account)                    # 触发 __str__
print(f"账户所有者：{account.owner}")
print(f"余额（像读属性一样）：{account.balance}")

account.Deposit(1500)
account.Withdraw(2000)

# 下面这行会报错，因为 setter 里有校验，取消注释可以自己试试
# account.balance = -100

# 私有属性其实被"改名"了，所以下面这行也会报错（这正是封装想达到的效果）
# Python 在编译时就把类体里所有 __xxx 形式的标识符自动改名成 _类名__xxx
# print(account.__balance)
# 但它并不是铁板一块，用"改名后的名字"依然能访问（Python 不强制私有）：
print(f"强行访问私有属性：{account._BankAccount__balance}")
print(f"历史记录（protected）：{account._history}") #py没有protected，只能说作者请你别碰，请自觉一点
print()


# ============================================================
# 第 3 步：继承 —— 复用父类的代码
# ============================================================
# 场景：储蓄账户和信用卡账户都是账户，都要有存款/取款，
# 但信用卡取款要收手续费。继承可以只写"不一样的那部分"。

class SavingsAccount(BankAccount):
    """储蓄账户：继承 BankAccount。

    C++ 里写 class SavingsAccount : public BankAccount
    Python 里写 class SavingsAccount(BankAccount)

    注意：父类叫"基类/父类"（base/parent class），
          子类叫"派生类"（derived class）。
    """

    def __init__(self, owner: str, balance: int = 0, rate: float = 0.03):
        # super() 调用父类的构造函数，对应 C++ 的 BaseClass(...)
        # 等价于 Python 2 时代的 BankAccount.__init__(self, owner, balance)
        super().__init__(owner, balance)
        self.rate = rate        # 年利率，子类独有的属性

    def AddInterest(self):
        """子类独有的方法：结算利息。"""
        interest = int(self.balance * self.rate)
        self.Deposit(interest)
        print(f"利息结算完成：按 {self.rate:.0%} 结算 {interest} 元")

    # 覆写纯靠同名，不用任何特殊标记
    def __str__(self) -> str:
        # 覆写（override）父类的 __str__，这就是"多态"的一种体现
        return f"<SavingsAccount owner={self.owner} balance={self.balance} rate={self.rate:.0%}>"


class CreditAccount(BankAccount):
    """信用卡账户：取款要收 1% 手续费。"""

    def __init__(self, owner: str, balance: int = 0, fee_rate: float = 0.01):
        super().__init__(owner, balance)
        self.fee_rate = fee_rate

    def Withdraw(self, amount: int) -> bool:
        """覆写父类的 Withdraw，加入手续费逻辑。

        关键点：想调用"父类原本的实现"用 super().Withdraw(...)，
        这样就不用把余额校验、历史记录这些代码再抄一遍（这就是继承的价值）。
        """
        fee = int(amount * self.fee_rate)
        total = amount + fee
        print(f"信用卡取款 {amount} 元，手续费 {fee} 元，共扣 {total} 元")
        return super().Withdraw(total)   # 复用父类的取款逻辑


print("=== 第 3 步：继承 ===")
saving = SavingsAccount("userB", 10000, rate=0.05)
print(saving)
saving.AddInterest()
print()

credit = CreditAccount("userC", 3000, fee_rate=0.02)
print(credit)
credit.Withdraw(1000)
print()

# isinstance / issubclass：判断"是什么类型"
# 对应 C++ 的 dynamic_cast / is_base_of，但 Python 里更加常用
print(f"saving 是 BankAccount 吗？ {isinstance(saving, BankAccount)}")
print(f"SavingsAccount 是 BankAccount 的子类吗？ {issubclass(SavingsAccount, BankAccount)}")
print()


# ============================================================
# 第 4 步：多态 —— 同一个接口，不同的实现
# ============================================================
# 这是 OOP 最重要的价值：调用方不用关心对方到底是哪种账户，
# 只要它"长得像账户"，就能统一处理。

def ProcessAll(accounts: List[BankAccount]):
    """统一处理一批账户。

    参数类型标注写的是父类 BankAccount，但实际可以传任何子类。
    运行时调用的 Withdraw 到底是哪一个，由对象的"真实类型"决定 —— 这就是多态。

    C++ 对比：这里等价于用 BaseClass* 的指针数组 + virtual 函数，
              但 Python 不需要写 virtual，方法默认就是"虚函数"。
    """
    print(f"--- 统一处理 {len(accounts)} 个账户 ---")
    for acc in accounts:
        print(acc)                  # 同样是 print，输出却不同（多态！）
        acc.Withdraw(500)
    print()


print("=== 第 4 步：多态 ===")
ProcessAll([
    BankAccount("普通户", 5000),
    SavingsAccount("储蓄户", 5000),
    CreditAccount("信用卡户", 5000),
])

# 鸭子类型（Duck Typing）：
# "如果它走起来像鸭子，叫起来也像鸭子，那它就是鸭子。"
# 下面这个类根本没继承 BankAccount，但只要它实现了同样的方法，
# ProcessAll 一样能处理它 —— Python 的多态不要求继承关系。
class Wallet:
    """一个"像账户"但毫无血缘关系的类。"""

    def __init__(self, money: int):
        self.money = money

    def __str__(self) -> str:
        return f"<Wallet money={self.money}>"

    def Withdraw(self, amount: int) -> bool:
        if amount > self.money:
            print(f"钱包余额不足：{self.money} 元")
            return False
        self.money -= amount
        print(f"钱包取现成功：{amount} 元，剩余 {self.money} 元")
        return True


print("--- 鸭子类型：Wallet 没有继承任何类，也能被统一处理 ---")
ProcessAll([Wallet(800)]) # 靠同名混过去了。。。
print()


# ============================================================
# 第 5 步：抽象基类 —— 强制子类实现接口
# ============================================================
# 上面的鸭子类型很自由，但"自由"的另一面是"没有约束"：
# 万一子类忘了实现 Withdraw 怎么办？运行时才会报错。
#
# 抽象基类（ABC）用来定义"契约"：子类必须实现指定的方法，否则实例化时就报错。
# 对应 C++ 的"纯虚函数 + 抽象类"。

from abc import ABC, abstractmethod # Abstract Base Class


class Shape(ABC):
    """抽象基类：不能直接 new，只能被继承。

    C++ 对比：
        class Shape {
        public:
            virtual double Area() const = 0;    // 纯虚函数
            virtual double Perimeter() const = 0;
        };
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def Area(self) -> float:
        """求面积。子类必须实现。"""
        raise NotImplementedError #抽象方法未实现的异常抛出

    @abstractmethod
    def Perimeter(self) -> float:
        """求周长。子类必须实现。"""
        raise NotImplementedError

    # 抽象类里也可以写"已经实现好的方法"，子类直接继承使用
    def Describe(self) -> str:
        return (f"{self.name}：面积 {self.Area():.2f}，"
                f"周长 {self.Perimeter():.2f}")


class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        super().__init__("矩形")
        self.width = width
        self.height = height

    def Area(self) -> float:
        return self.width * self.height

    def Perimeter(self) -> float:
        return 2 * (self.width + self.height)


class Circle(Shape):
    def __init__(self, radius: float):
        super().__init__("圆")
        self.radius = radius

    def Area(self) -> float:
        # 用 math.pi 更规范，这里为了一行写完直接用 3.1415926
        return 3.1415926 * self.radius ** 2

    def Perimeter(self) -> float:
        return 2 * 3.1415926 * self.radius


print("=== 第 5 步：抽象基类 ===")
shapes: List[Shape] = [Rectangle(3, 4), Circle(5)]
for shape in shapes:
    print(shape.Describe())     # 同样调用 Describe，Area 结果各不相同（多态）
print()

# 下面这行会直接报 TypeError，因为 Shape 是抽象类，且有未实现的抽象方法
# shape = Shape("未知")
# 同理，子类如果漏掉 Area/Perimeter 也会在实例化时报错 —— 这就是"契约"的作用
print()


# ============================================================
# 第 6 步：魔术方法 —— 让自己的类用起来像内置类型 （可以跳过留个印象就好）
# ============================================================
# 对应 C++ 的运算符重载：operator+、operator[]、operator== 等等。

class Vector2D:
    """二维向量：演示常见的魔术方法。

    让自定义对象支持 + - * == len() 等语法，
    代码读起来就跟内置类型一样自然。
    """

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __repr__(self) -> str:
        return f"Vector2D({self.x}, {self.y})"

    # 加法：对应 C++ 的 operator+
    def __add__(self, other: "Vector2D") -> "Vector2D":
        return Vector2D(self.x + other.x, self.y + other.y)

    # 减法：对应 C++ 的 operator-
    def __sub__(self, other: "Vector2D") -> "Vector2D":
        return Vector2D(self.x - other.x, self.y - other.y)

    # 相等：对应 C++ 的 operator==
    def __eq__(self, other) -> bool:
        if not isinstance(other, Vector2D):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    # 让对象可以像列表一样用下标访问：v[0]、v[1]
    # 对应 C++ 的 operator[]
    def __getitem__(self, index: int) -> float:
        if index == 0:
            return self.x
        if index == 1:
            return self.y
        raise IndexError(f"Vector2D 只有 2 个分量，索引 {index} 越界")

    # 支持 len(v)
    def __len__(self) -> int:
        return 2

    # 支持迭代：for v in vector
    def __iter__(self):
        yield self.x
        yield self.y


print("=== 第 6 步：魔术方法 ===")
v1 = Vector2D(1, 2)
v2 = Vector2D(3, 4)
print(f"v1 = {v1}, v2 = {v2}")
print(f"v1 + v2 = {v1 + v2}")
print(f"v2 - v1 = {v2 - v1}")
print(f"v1 == Vector2D(1, 2) ？ {v1 == Vector2D(1, 2)}")
print(f"v1[0] = {v1[0]}, v1[1] = {v1[1]}")
print(f"len(v1) = {len(v1)}")
print(f"迭代 v1：{list(v1)}")
print()


# ============================================================
# 第 7 步：类方法 与 静态方法
# ============================================================
# 三种方法的区别（面试常考）：
#     实例方法：def f(self)         —— 绑定到对象，能访问 self
#     类方法  ：@classmethod def f(cls)  —— 绑定到类，能访问 cls，常用于"备用构造函数"
#     静态方法：@staticmethod def f()    —— 谁都不绑定，就是个"放在类里的普通函数"
#
# C++ 对比：
#     实例方法  ≈ 普通成员函数
#     类方法    ≈ static 成员函数（但能访问类级别的属性、能多态）
#     静态方法  ≈ 命名空间里的自由函数

class Date:
    """日期类：演示三种方法和"备用构造函数"模式。"""

    # 类属性：记录所有 Date 对象的个数
    total: int = 0

    def __init__(self, year: int, month: int, day: int):
        self.year = year
        self.month = month
        self.day = day
        Date.total += 1

    def __str__(self) -> str:
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"

    # ---------- 类方法：备用构造函数 ----------
    @classmethod
    def FromString(cls, text: str) -> "Date":
        """从 "2026-10-01" 这样的字符串创建对象。

        为什么用 cls 而不是写死 Date？
        因为子类调用时 cls 会是子类，这样"备用构造函数"可以被子类继承复用。
        注意返回的是 cls(...) 而不是 Date(...)，这是精髓。
        """
        year, month, day = (int(x) for x in text.split("-"))
        return cls(year, month, day) # 注意：如果子类改了构造函数的参数表，如果没有默认参数填充多余的或是格式不对直接爆炸，此时子类应该负责提供工厂方法

    @classmethod
    def Today(cls) -> "Date":
        """今天。同样返回 cls(...)，子类调用会创建子类对象。"""
        import datetime
        now = datetime.date.today()
        return cls(now.year, now.month, now.day)

    # ---------- 静态方法：跟对象状态无关的工具函数 ----------
    @staticmethod
    def IsLeapYear(year: int) -> bool:
        """判断闰年。不需要 self，也不需要 cls，纯计算。

        写成静态方法而不是普通函数，是为了"从属关系清晰"：
        Date.IsLeapYear(2024) 一眼就知道这是日期相关的能力。
        """
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


print("=== 第 7 步：类方法与静态方法 ===")
d1 = Date(2026, 10, 1)
d2 = Date.FromString("2024-02-29")      # 类方法当备用构造函数用
d3 = Date.Today()
print(f"直接构造：{d1}")
print(f"从字符串构造：{d2}")
print(f"今天：{d3}")
print(f"2024 是闰年吗？ {Date.IsLeapYear(2024)}")
print(f"当前 Date 对象总数：{Date.total}")
print()


# ============================================================
# 第 8 步：综合小练习 —— 用 OOP 重写一个迷你银行系统
# ============================================================
# 把前面的知识串起来：抽象基类 + 继承 + 多态 + 封装 + 魔术方法。
#
# 对比你 Homework2 里用"模块级全局变量 + 一堆函数"的写法，
# 这里每个对象自己管理自己的状态，没有 global，也不会互相污染。

class Transaction(ABC):
    """交易记录（抽象基类）。"""

    def __init__(self, amount: int):
        self.amount = amount

    @abstractmethod
    def Apply(self, account: "Account") -> bool:
        """把本笔交易作用到账户上，返回是否成功。"""
        raise NotImplementedError

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.amount})"


class DepositTransaction(Transaction):
    """存款交易。"""

    def Apply(self, account: "Account") -> bool:
        account._balance += self.amount          # 同类族内部访问受保护属性
        account._records.append(f"存款 {self.amount}")
        return True


class WithdrawTransaction(Transaction):
    """取款交易。"""

    def Apply(self, account: "Account") -> bool:
        if self.amount > account._balance:
            account._records.append(f"取款 {self.amount} 失败（余额不足）")
            return False
        account._balance -= self.amount
        account._records.append(f"取款 {self.amount}")
        return True


class Account:
    """账户：自己管理自己的余额和流水。

    和你 Homework2 的写法对比：
        Homework2：currentUser 是模块级全局变量，谁都能改；
        这里     ：每笔余额都存在各自的 Account 对象里，互不干扰。
    """

    def __init__(self, owner: str, balance: int = 0):
        self.owner = owner
        self._balance = balance
        self._records: List[str] = []

    @property
    def balance(self) -> int:
        return self._balance

    def Execute(self, txn: Transaction) -> bool:
        """执行一笔交易。

        注意：这里完全不用 if/else 判断"这是存款还是取款"，
        直接让交易对象自己去 Apply —— 新增交易类型时，这个方法一个字都不用改。
        这就是"对扩展开放、对修改关闭"（开闭原则）。
        """
        ok = txn.Apply(self)
        status = "成功" if ok else "失败"
        print(f"[{self.owner}] {txn} 执行{status}，余额 {self._balance}")
        return ok

    def ShowRecords(self):
        print(f"[{self.owner}] 流水：")
        for i, record in enumerate(self._records, start=1):
            print(f"    {i}. {record}")

    def __str__(self) -> str:
        return f"<Account owner={self.owner} balance={self._balance}>"


print("=== 第 8 步：综合示例（迷你银行）===")
acc = Account("userA", 5000)
print(acc)

# 统一用 Execute 驱动，交易类型由对象自己决定 —— 多态的威力
for txn in [
    DepositTransaction(1500),
    WithdrawTransaction(2000),
    WithdrawTransaction(99999),     # 余额不足，会失败
    DepositTransaction(300),
]:
    acc.Execute(txn)

acc.ShowRecords()
print()


# ============================================================
# 总结：Python OOP vs C++ OOP 速查表
# ============================================================
# ┌────────────────────┬──────────────────────────┬────────────────────────────┐
# │ 概念               │ C++                      │ Python                     │
# ├────────────────────┼──────────────────────────┼────────────────────────────┤
# │ 成员变量声明        │ 类里显式声明              │ self.x = x 赋值即声明       │
# │ 构造函数            │ ClassName(...)           │ __init__(self, ...)        │
# │ 析构函数            │ ~ClassName()             │ __del__（一般不用，靠 GC）  │
# │ this 指针           │ 隐式 this                │ 显式 self（必须写）         │
# │ 访问控制            │ public/protected/private │ 靠 _ / __ 约定，非强制      │
# │ 继承                │ class A : public B       │ class A(B)                 │
# │ 调用父类构造函数     │ BaseClass(...)           │ super().__init__(...)      │
# │ 虚函数              │ 需要写 virtual            │ 默认全是虚函数              │
# │ 纯虚函数/抽象类      │ = 0                     │ @abstractmethod + ABC      │
# │ 运算符重载          │ operator+                │ __add__、__eq__ 等魔术方法  │
# │ 常量                │ const                    │ 全大写命名约定              │
# │ 静态成员            │ static                   │ 类属性 / @classmethod       │
# │ 类型判断            │ dynamic_cast / typeid    │ isinstance / type           │
# └────────────────────┴──────────────────────────┴────────────────────────────┘
