# 农产品质量安全全链数据服务MCP server

## 概述
以农产品质量安全要素为核心，通过19个符合MCP协议标准的API接口，提供涵盖农药基础信息数据；农药、肥料进货销售数据；农产品质量安全监测数据；农产品承诺达标合格开具数据等全链条数据支撑服务。

依赖MCP Python SDK开发，任意支持MCP协议的智能体助手（如Claude、Cursor以及Cherry Studio等）都可以快速接入。

## 工具
### 农药基本信息 getNyInfo
根据农药名称和登记证号获取农药的基本信息。
### **输入**:
- `name` 农药
- `djzh` 登记证号
### **输出**:
农药基本信息，包含`name`, `jix`,`yxqz`等

### 农药成分 getNyChengF
根据农药名称和登记证号获取农药的主要成分。
### **输入**:
- `name` 农药
- `djzh` 登记证号
### **输出**：
农药成分，包含`name_cn`, `hanl`等

### 农药生产企业 getNyShengCQY
根据农药名称和登记证号获取农药的生产企业。
### **输入**:
- `name` 农药
- `djzh` 登记证号
### **输出**：
生产企业，包含`name`, `addr`,`contact`,`phone`等

### 农药使用范围和使用方法 getNyUseInfo
根据农药名称和登记证号获取农药的使用范围和使用方法。
### **输入**:
- `name` 农药
- `djzh` 登记证号
### **输出**：
使用范围和使用方法，包含`crops`, `fzdx`,`dosage`,`syff`等

### 生产企业生产哪些农药 getNyInfoByScqy
根据生产企业获取该生产企业生产哪些农药。
### **输入**:
- `scqy` 生产企业
### **输出**：
农药名称，包含`name`等

### 农作物病虫害防治药物 getFzffByCropFzdx
根据农作物名称和病虫害名称获取防治药物及使用方法。
### **输入**:
- `crop` 农作物
- `fzdx` 病虫害
### **输出**：
防治药物及使用方法，包含`name`, `dosage`,`syff`等

### 农作物适宜气候及城市 getPlantWeather
根据农作物名称获得该农作物适合的种植气候以及包含城市。
### **输入**:
- `plant` 农作物
### **输出**：
气候及城市，包含`weather`, `city`等

### 城市气候及适合种植作物 getCityWeather
根据城市名称获得该城市的气候以及适合种植的作物。
### **输入**:
- `city` 城市
### **输出**：
气候及作物，包含`weather`, `plant`等

### 农产品药物检出限 get_medication_value
根据农产品名称和药物名称，获得该农产品上的该药物的检出限(检出上限)。
### **输入**:
- `productName` 农产品
- `medicationName` 药物
### **输出**:
检出限，包含`name`, `value`, `unit`等

### 检测合格率 get_monitor_info
根据年度，区划，农产品名称获得该地区该农产品的检测合格率。
### **输入**:
- `year` 年度
- `areaName` 区划
- `cpname` 农产品名称
### **输出**:
合格率，包含`all_num`, `qualified_num`, `qualified_rat`等

### 风险农产品 get_risk_agricultural_products
根据年度，区划，获得该地区检测合格率较低的农产品。
### **输入**:
- `year` 年度
- `areaName` 区划
### **输出**:
农产品名称，包含`name`等

### 合格证开具批次 get_hgz_num
根据年度，区划,产品名称，获得该地区合格证开具批次数量。
### **输入**:
- `year` 年度
- `areaName` 区划
- `cpname` 产品名称
### **输出**:
开具批次数量，包含`num`,`dyzs`等

### 农资产品进货量销售量 get_sale_buy_num
根据年度，区划,产品名称，获得该地区合格证开具批次数量。
### **输入**:
- `year` 年度
- `areaName` 区划
- `name` 产品名称/产品分类
### **输出**:
进货量销售量，包含`totalSale`,`totalBuy`等

### 农资店及农资产品 getNzdByYpName
根据地区，农资产品，获得该地区售卖该农资产品的农资店信息和农资产品信息。
### **输入**:
- `areaName` 区划
- `name` 农资产品
### **输出**:
农资店及农资产品信息，包含`nzdname`,`nzdaddress`,`nzdlxdh`等

### 主推配方肥 getZtfp
根据地区，年度，获得该地区主推配方肥流通量。
### **输入**:
- `areaName` 区划
- `year` 年度
### **输出**:
主推配方肥流通量，包含`year`,`at`等

### 农事指导信息 get_agricultural_guidance_vector
根据用户问题，获得农事指导意见。
### **输入**:
- `text` 问题
### **输出**:
农事指导意见，包含`content`等

### 病虫测报信息 get_agricultural_disease_report_vector
根据用户问题，获得病虫测报信息。
### **输入**:
- `text` 问题
### **输出**:
病虫测报，包含`content`等

### 农业典型案例信息 get_agricultural_case_vector
根据用户问题，获得农业典型案例信息。
### **输入**:
- `text` 问题
### **输出**:
农业典型案例信息，包含`content`等

### 农作物生长模式信息 get_agricultural_growth_model_vector
根据用户问题，获得农作物生长模式信息。
### **输入**:
- `text` 问题
### **输出**:
农作物生长模式信息，包含`content`等



## 开始使用
使用农产品质量安全全链数据服务MCP Server主要是用Python，下面开始介绍。

### 获取KEY
通过KEY你才能够调用农产品质量安全全链数据服务MCP Server能力，请联系0571-88816415获取。

### Python接入
我们通过pypi发布了农产品质量安全全链数据服务MCP Server：`hzzzwl-agriculture-mcp-x`，你可以使用任意Python包管理工具轻松获取并快速配置使用。

### 安装
使用uv时不需要特殊安装，我们将使用uvx直接运行`hzzzwl-agriculture-mcp-x`

### 配置
在任意MCP客户端（如Claude.app）中添加如下配置，部分客户端下可能需要做一些格式化调整。
```json
{
  "mcpServers": {
    "hzzzwl-agriculture-mcp-x": {
      "command": "uvx",
      "args": ["hzzzwl-agriculture-mcp-x"],
      "env": {
        "KEY": "<YOUR_API_KEY>"
      }
    }
  }
}
```
其中YOUR_API_KEY对应的值需要替换为你自己的KEY。保存配置后，重启你的MCP客户端，即可使用农产品质量安全全链数据服务MCP Server。

### 示例
#### 问题：
柑橘树有红蜘蛛要用什么药，我在义乌市，我该去哪些农资店买药呢
#### 工具调用：
- getFzffByCropFzdx
- getNzdByYpName
#### 答案：
柑橘树红蜘蛛可以使用以下药剂进行防治，推荐的药剂及用法如下：

#### 推荐药剂
- 联肼·螺虫酯（2000-3000倍液，喷雾）
- 炔螨特（1000-1350倍液，喷雾）
- 甲氰·噻螨酮（750-1000倍液，喷雾）
- 阿维·矿物油（1000-2000倍液，喷雾）
- 阿维·哒螨灵（1500-2000倍液，喷雾）
- 阿维菌素（4000-5000倍，喷雾）
- 阿维·炔螨特（1000-1500倍液，喷雾）

#### 购买农资店
在义乌市，您可以购买到“阿维菌素”这一药剂，以下是部分农资店信息：
##### 义乌市苏溪供销合作社东塘分社
- 地址：xxx
- 电话：xxx
- 规格：xxx，价格xxx，库存xxx
##### 义乌市圣穗供销农资连锁有限公司赤岸经营部
- 地址：xxx
- 电话：xxx
- 规格：xxx，价格xxx，库存xxx
##### 义乌市苏溪供销合作社巧溪分社
- 地址：xxx
- 电话：xxx
- 规格：xxx，价格xxx，库存xxx
##### 义乌市圣穗供销农资连锁有限公司塔山经营部
- 地址：xxx
- 电话：xxx
- 规格：xxx，价格xxx，库存xxx
##### 义乌市圣穗供销农资连锁有限公司毛店经营部
- 地址：xxx
- 电话：xxx
- 规格：xxx，价格xxx，库存xxx

建议您前往上述农资店购买“阿维菌素”进行防治。如需其他药剂，可以继续帮您查询。使用时请严格按照说明书或推荐剂量兑水喷雾，注意安全防护。


