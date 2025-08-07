# ZuoBiao_Point_Check_In

# 小米运动自动刷步数

> ZuoBiao自动刷积分

## Github Actions 部署指南

### 一、Fork 此仓库

### 二、设置账号密码
# 新增
添加名为  **CONFIG**的变量: Settings-->Secrets-->New secret ,使用下面json模板配置多账户，支持邮箱,手机号
```
{
  "ZUOBIAO": [
            {
                "account": "XXXX",
                "password": "XXXX"
            }
        ]
}
```
> 添加名为  **PAT** 的变量: Settings-->Secrets-->New secret

| Secrets |  格式  |
| -------- | ----- |
| PAT |   此处**PAT**需要申请，值为github token，教程详见：https://www.jianshu.com/p/bb82b3ad1d11 ,需要repo和workflow权限,此项必填，避免git push的权限错误。 |