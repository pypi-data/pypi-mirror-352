# Cryptopian Infrastructure

## Application Secret Management with 1password
### 设计
1. 每个APP只需要设置两个环境变量，就可以从1password service拿到所有的app secrets
2. readonly/trade api都放在1password里面，通过ApiManager拿到
3. 公用的服务都可以在拿到secrets之后马上返回实例
   1. InfluxFactory
   2. MongoFactory
   3. SlackFactory

### 部署
1. 1password connect
2. Mongo DB
3. Influx DB