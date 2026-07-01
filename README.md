# 外卖点餐系统（Sky Take-Out）帮助文档

---

## 一、项目概述

**Sky Take-Out** 是一个基于 Spring Boot 的外卖点餐管理系统，分为两个端：

- **管理端（Admin）**：面向商家/管理员，负责菜品管理、订单处理、数据统计等
- **用户端（User）**：面向消费者，负责浏览菜品、下单、购物车、订单管理等

系统前端采用微信小程序，后端提供 RESTful API 接口。

---

## 二、技术栈

| 技术/框架 | 版本 | 用途 |
|-----------|------|------|
| Spring Boot | 2.7.3 | 核心框架 |
| MyBatis | 2.2.0 | ORM 持久层框架 |
| MyBatis PageHelper | 1.3.0 | 分页插件 |
| Druid | 1.2.1 | 数据库连接池 |
| Spring Cache + Redis | — | 数据缓存 |
| JWT (jjwt) | 0.9.1 | 身份认证令牌 |
| Alibaba Cloud OSS | 3.10.2 | 对象存储（图片上传） |
| WeChat Pay | 0.4.8 | 微信支付 |
| Baidu Map API | — | 地址定位、距离计算 |
| Knife4j | 3.0.2 | API 在线文档（Swagger） |
| Spring Task | — | 定时任务 |
| WebSocket | — | 实时消息推送（催单） |
| Apache POI | 3.16 | Excel 报表导出 |
| Lombok | 1.18.30 | 简化代码 |
| Fastjson | 1.2.76 | JSON 序列化 |

### 数据库

- **MySQL**：主数据库，存储所有业务数据
- **Redis**：缓存数据库，存储验证码、菜品分类、购物车等

---

## 三、项目结构

```
sky-take-out/
├── pom.xml                          # 父 POM（Maven 多模块）
├── sky-common/                      # 公共模块（通用工具类、异常、常量等）
│   └── src/main/java/com/sky/
│       ├── constant/                # 常量类（JWT、消息、状态等）
│       ├── context/                 # 线程上下文（BaseContext）
│       ├── enumeration/             # 枚举（操作类型）
│       ├── exception/               # 自定义异常
│       ├── json/                    # JSON 序列化配置
│       ├── properties/              # 配置属性类
│       ├── result/                  # 统一响应结果
│       └── utils/                   # 工具类（JWT、OSS、HTTP、微信支付等）
├── sky-pojo/                        # 数据传输对象模块
│   └── src/main/java/com/sky/
│       ├── dto/                     # 请求参数 DTO
│       ├── entity/                  # 数据库实体类
│       └── vo/                      # 响应视图对象
└── sky-server/                      # 服务启动模块
    ├── src/main/java/com/sky/
    │   ├── SkyApplication.java      # 启动类
    │   ├── Aspect/                  # AOP 切面（自动填充）
    │   ├── annotation/              # 自定义注解
    │   ├── config/                  # 配置类（OSS、Redis、WebMVC 等）
    │   ├── controller/admin/        # 管理端控制器
    │   ├── controller/user/         # 用户端控制器
    │   ├── handler/                 # 全局异常处理
    │   ├── interceptor/             # JWT 拦截器
    │   ├── mapper/                  # MyBatis Mapper 接口
    │   ├── service/                 # 业务逻辑接口
    │   ├── service/impl/            # 业务逻辑实现
    │   ├── task/                    # 定时任务
    │   └── websocket/               # WebSocket 服务
    └── src/main/resources/
        ├── application.yml           # 主配置文件
        ├── application-dev.yml       # 开发环境配置
        └── mapper/                   # MyBatis XML 映射文件
```

---

## 四、数据库设计

### 核心数据表

| 表名 | 说明 | 关键字段 |
|------|------|----------|
| employee | 员工（管理员）表 | id, username, password, name, status, role |
| user | 用户（C端）表 | id, openid, name, phone |
| category | 菜品分类表 | id, type, name, sort, status |
| dish | 菜品表 | id, category_id, name, price, image, description, status |
| dish_flavor | 菜品口味表 | id, dish_id, name, value |
| setmeal | 套餐表 | id, category_id, name, price, status |
| setmeal_dish | 套餐菜品关联表 | id, setmeal_id, dish_id |
| shopping_cart | 购物车表 | id, user_id, dish_id, dish_flavor, number |
| address_book | 地址簿 | id, user_id, phone, address, is_default |
| orders | 订单表 | id, number, user_id, address_book_id, status, amount, pay_status |
| order_detail | 订单明细表 | id, order_id, dish_id, dish_flavor, number, amount |

### 订单状态（Orders 常量）

| 状态码 | 状态名称 | 说明 |
|--------|----------|------|
| 1 | 待付款（PENDING_PAYMENT） | 用户提交订单待支付 |
| 2 | 待接单（PENDING_CONFIRM） | 已支付等待商家确认 |
| 3 | 已接单/待派送（CONFIRMED） | 商家已确认，等待配送 |
| 4 | 配送中（DELIVERY_IN_PROGRESS） | 骑手配送中 |
| 5 | 已完成（COMPLETED） | 订单已完成 |
| 6 | 已取消（CANCELLED） | 订单已取消 |
| 7 | 已退款（REFUND） | 已退款 |

### 支付状态

| 状态码 | 说明 |
|--------|------|
| 0 | 未支付 |
| 1 | 已支付 |

---

## 五、功能模块详解

### 5.1 管理端功能（/admin/*）

#### 员工管理
- 登录 / 退出
- 新增员工、编辑员工、分页查询员工列表
- 启用/禁用员工账号

#### 菜品分类管理
- 新增、编辑、删除、查询分类
- 按 type 区分（菜品分类 / 套餐分类）
- 启用/禁用分类

#### 菜品管理
- 新增/编辑菜品（含口味设置、图片上传至 OSS）
- 菜品分页查询
- 菜品启售/停售
- 菜品删除（与套餐关联时不可删）

#### 套餐管理
- 新增/编辑套餐（关联多个菜品）
- 套餐启售/停售
- 套餐分页查询

#### 订单管理
- 查看所有订单列表
- 接单 / 拒单
- 派送订单（转配送中）
- 订单详情查看

#### 数据统计（报表）
- 营业额统计（按日期范围）
- 用户数据统计
- 订单数据统计
- 销量 Top10 菜品
- 导出 Excel 报表

#### 工作台（WorkSpace）
- 工作台概览数据（今日订单数、今日营业额、待处理订单数等）
- 订单概览数据（各状态订单数量）

### 5.2 用户端功能（/user/*）

#### 用户登录
- 微信授权登录（获取 openid）

#### 地址管理
- 新增地址、编辑地址、删除地址
- 查询地址列表、设置默认地址

#### 菜品浏览
- 分类查询
- 菜品列表查询（含起售/停售筛选）
- 套餐列表查询

#### 购物车
- 添加菜品到购物车
- 减少/清空购物车
- 查看购物车列表

#### 订单管理
- 提交订单（自动计算金额、检查地址）
- 查看历史订单（分页）
- 订单详情
- 取消订单
- 再来一单（快速复制旧订单）
- 订单催单（WebSocket 实时通知）

#### 我的
- 个人中心
- 用户管理（编辑个人信息）

---

## 六、核心功能实现说明

### 6.1 认证机制

系统采用 **JWT（JSON Web Token）** 实现无状态身份认证：

- **管理端**：登录成功后生成 JWT 令牌（token 名称: `token`，有效期: 24 小时），放在请求头中
- **用户端**：登录成功后生成 JWT 令牌（token 名称: `authentication`，有效期: 24 小时）
- 分别通过 `JwtTokenAdminInterceptor` 和 `JwtTokenUserInterceptor` 进行拦截校验

### 6.2 自动填充（AOP）

采用 AOP 切面实现公共字段（创建时间、更新时间、创建人、更新人）的自动填充：
- 注解 `@AutoFill(OperationType.INSERT)` — 新增时自动填充
- 注解 `@AutoFill(OperationType.UPDATE)` — 更新时自动填充

### 6.3 定时任务

| 任务 | 执行频率 | 功能 |
|------|----------|------|
| 订单超时取消 | 每分钟 | 取消超过 15 分钟未支付的订单 |
| 自动确认完成 | 每天凌晨 1 点 | 将超过 1 小时仍在配送中的订单标记为已完成 |

### 6.4 WebSocket 催单通知

- 用户可通过 WebSocket 连接向商家催单
- 服务端收到催单消息后，向所有连接的客户端广播通知

### 6.5 文件上传

使用阿里云 OSS（对象存储服务）存储菜品、套餐图片：
- 统一上传接口 `/admin/common/upload`
- 配置项：bucket-name: `java-sky-take-web`，endpoint: `oss-cn-beijing.aliyuncs.com`

### 6.6 地址定位

接入百度地图 API 实现地址解析和距离计算。

### 6.7 Excel 导出

支持导出运营数据报表（营业额、用户、订单统计），通过 Apache POI 实现。

---

## 七、环境要求

| 组件 | 要求 |
|------|------|
| JDK | 1.8 或更高 |
| Maven | 3.6+ |
| MySQL | 5.7+ |
| Redis | 5.0+ |
| IDE | IntelliJ IDEA / Eclipse |

---

## 八、快速启动步骤

### 步骤 1：克隆/导入项目
```bash
# 使用 IDE（推荐 IntelliJ IDEA）打开项目目录
C:\Java_code\sky-take-out
```

### 步骤 2：准备数据库
1. 创建数据库 `sky_take_out`
2. 导入 SQL 脚本（需自行准备，表结构包含员工表、用户表、菜品分类、菜品、套餐、购物车、地址、订单等）
3. 修改数据库密码（如非默认 `1234`），编辑：
   ```
   sky-server/src/main/resources/application-dev.yml
   ```

### 步骤 3：安装依赖
```bash
mvn clean install
```

### 步骤 4：启动服务
```bash
# 方式一：IDE 直接运行 SkyApplication.main() 方法
# 方式二：Maven 启动
mvn spring-boot:run -pl sky-server
```

### 步骤 5：访问 API 文档
启动成功后访问：
```
http://localhost:8080/doc.html
```
通过 Knife4j 可在浏览器中查看和测试所有接口。

### 步骤 6：配置外部服务（如需）

编辑 `application-dev.yml` 中的以下配置：
- 阿里云 OSS（用于图片上传）
- 微信支付参数
- 百度地图 API Key
- Redis 密码

---

## 九、主要接口速查

### 管理端接口（/admin/*）

| 模块 | 路径前缀 | 核心接口 |
|------|----------|----------|
| 员工 | `/admin/employee` | 登录、新增、编辑、分页查询、启用/禁用 |
| 分类 | `/admin/category` | 新增、编辑、删除、启/停用、分页查询 |
| 菜品 | `/admin/dish` | 新增、编辑、启/停售、分页查询、批量删除 |
| 套餐 | `/admin/setmeal` | 新增、编辑、启/停售、分页查询、删除 |
| 订单 | `/admin/order` | 查询列表、接单、拒单、派送、详情、取消 |
| 报表 | `/admin/report` | 营业额统计、用户统计、订单统计、Top10、导出 |
| 工作台 | `/admin/workspace` | 概览数据、订单概览 |
| 通用 | `/admin/common` | 图片上传 |

### 用户端接口（/user/*）

| 模块 | 路径前缀 | 核心接口 |
|------|----------|----------|
| 用户 | `/user/user` | 登录 |
| 地址 | `/user/addressBook` | CRUD、设置默认 |
| 分类 | `/user/category` | 查询分类列表 |
| 菜品 | `/user/dish` | 按分类查询菜品 |
| 套餐 | `/user/setmeal` | 查询套餐列表 |
| 购物车 | `/user/shoppingCart` | 添加、减少、清空、查询 |
| 订单 | `/user/order` | 下单、支付、历史订单、详情、取消、再来一单、催单 |
| 我的 | `/user` | 编辑个人信息 |

---

## 十、开发规范与注意事项

1. **统一响应格式**：所有接口返回 `Result` 对象，包含 `code`、`msg`、`data` 字段
2. **分页**：使用 `PageHelper` 插件，请求参数中传入 `page` 和 `pageSize`
3. **事务管理**：开启注解事务（`@EnableTransactionManagement`）
4. **密码加密**：员工密码存储需加密
5. **状态管理**：启用/禁用、启售/停售等均通过 `status` 字段控制（1=启用/启售，0=禁用/停售）
6. **图片上传**：菜品、套餐图片统一通过 OSS 上传，接口返回图片 URL
7. **日期格式**：报表接口接收 `yyyy-MM-dd` 格式日期参数
8. **全局异常处理**：自定义异常统一在 `GlobalExceptionHandler` 中捕获处理

---

## 十一、配置文件说明

```
sky-server/src/main/resources/
├── application.yml          # 主配置（服务端口、数据源、Redis、MyBatis、JWT、OSS 等）
└── application-dev.yml      # 开发环境配置（数据库连接、OSS、微信、百度地图等）
```

### 关键配置项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `server.port` | 服务端口 | 8080 |
| `spring.profiles.active` | 激活的环境 | dev |
| `sky.datasource.*` | MySQL 连接配置 | host: localhost, db: sky_take_out |
| `sky.redis.*` | Redis 连接配置 | host: localhost, port: 6379 |
| `sky.jwt.admin-secret-key` | 管理端 JWT 签名密钥 | itcast |
| `sky.jwt.user-secret-key` | 用户端 JWT 签名密钥 | itheima |
| `sky.alioss.*` | 阿里云 OSS 配置 | 需自行申请 |
| `sky.wechat.appid/secret` | 微信小程序 AppID/Secret | 需自行申请 |
| `sky.baidu.ak` | 百度地图 API Key | 需自行申请 |

---

## 十二、常见问题

**Q1: 数据库密码在哪里修改？**
> 修改 `sky-server/src/main/resources/application-dev.yml` 中的 `sky.datasource.password`

**Q2: 如何切换环境？**
> 修改 `spring.profiles.active` 的值，可添加 `application-prod.yml` 生产环境配置文件

**Q3: 接口文档打不开？**
> 确保服务已启动，访问 `http://localhost:8080/doc.html`，需确保不与其他服务端口冲突

**Q4: Redis 连接失败？**
> 检查 Redis 是否已启动，确认 `application-dev.yml` 中密码配置正确

**Q5: 图片上传失败？**
> 检查阿里云 OSS 配置（AccessKey、Bucket、Endpoint）是否正确

**Q6: 如何部署到生产环境？**
> 1. 修改 `application-prod.yml` 配置生产数据库和 Redis
> 2. 打包：`mvn clean package -DskipTests`
> 3. 运行：`java -jar sky-server/target/sky-server-1.0-SNAPSHOT.jar`

---

## 十三、联系与版权

本项目为学习项目，技术栈来自黑马程序员 Java 实战课程。
---

*文档生成日期：2026-07-01*
