# xiechengspider

这是一个携程的机票爬虫，如有侵犯可以联系

起点城市编号
start_city_list = []

目的地城市编号
end_city_list = []

start、end为查找的机票日期周期

生成结果是dataframe形式的，因为是帮女朋友拉取的数据因此放到了excel表格里面

对应的就是一趟行程中的航线（因为这批都比较少直飞，因此会有两程航线），后面的价格由于仓位不同还会有多列数据
