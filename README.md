# Timestream 压测工具及方法


## 免责声明
建议测试过程中使用此方案，生产环境使用请自行考虑评估。
当您对方案需要进一步的沟通和反馈后，可以联系 nwcd_labs@nwcdcloud.cn 获得更进一步的支持。
欢迎联系参与方案共建和提交方案需求, 也欢迎在 github 项目 issue 中留言反馈 bugs。

## 压测方法
1. 打开 AWS console，在您希望的目标区域创建 timestream 以及 kinesis。 注：Timestream目前并未在所有的 AWS 区域上线，所有上线的区域请查看[此页面](https://aws.amazon.com/cn/timestream/pricing/),本文用的是 N.Virginia (us-east-1)区域.
1. 在 Timestream 当中创建一个数据库，名为 ``kdaflink`` 。[点击查看创建方法](https://docs.aws.amazon.com/zh_cn/timestream/latest/developerguide/console_timestream.html#console_timestream.db.using-console)
1. 创建一个 table 名为 ``kinesisdata1``。[点击查看创建方法](https://docs.aws.amazon.com/zh_cn/timestream/latest/developerguide/console_timestream.html#console_timestream.table.using-console)。注意：在这一步中，会设置数据从内存到磁性的生命周期。我们可以设置一个方便测试的数值，观测不同的存储介质对于查询的影响。
1. 创建一个 kinesis data stream 名为 ``TimestreamTestStream``。[点击查看创建方法](https://docs.aws.amazon.com/streams/latest/dev/amazon-kinesis-streams.html#how-do-i-create-a-stream)
1. 启动一台服务器 EC2， ``git clone`` 将此 repo 下载到到服务器上。
1. 确保您的服务器已经安装了 [maven](https://maven.apache.org/install.html)，您可以通过 ``mvn -version`` 来验证是否安装。
1. 下载并安装 flink   
   ```
   wget https://archive.apache.org/dist/flink/flink-1.8.2/flink-1.8.2-src.tgz
   tar -xvf flink-1.8.2-src.tgz
   cd flink-1.8.2
   mvn clean install -Pinclude-kinesis -DskipTests
   ```
 1. 到 ``flink_connector `` 这个目录下编译并运行。这样 flink connector 就可以启动起来。如果您之前采用了的不同的 timestream database 和 table 的名称，请记得替换变量。
    ```
    # cd ~/timestream-scale-performance/flink_connector
    mvn clean compile
    mvn exec:java -
    Dexec.mainClass="com.amazonaws.services.kinesisanalytics.StreamingJob" -
    Dexec.args="--InputStreamName TimestreamTestStream --Region us-east-1 --
    TimestreamDbName kdaflink --TimestreamTableName kinesisdata1"
    ```

 1. 保持此窗口不变。新建一个 terminal，或者新启动一台 EC2，确保此服务器已经安装 ``python3``。
 1. 运行 producer 的程序，以模拟设备生产数据。其中 ``stream`` 的参数是用来指定 kinesis stream的，如果您在前序步骤中改变了 stream 的名称，请记得替换； ``region`` 参数为您的 timestream 以及 kinesis 所在的区域，如您使用的是其他区域，请记得替换。    
    ```
    # cd ~/timestream-scale-performance  回到此repo主目录下
    python3 timestream_kinesis_data_gen_blog.py --stream TimestreamTestStream --region us-east-1
    ```     
 1. 此时，如无错误，``Amazon Timestream ``将持续被写入数据。可以在 ``kinesis`` 的监控，``Amazon Timestream``  监控中，观察写入延迟等指标。也可以在 ``Amazon Timestream``  中，通过 ``count`` 的方式查询写入条数。当观测达到目标数量级时，停止写入。
 1. 在后续测试中，我们会有一个JOIN的延迟测试，为了方便准备测试环境，创建一张与原表数据格式相同的表，命名为 ``kinesis600``，重复上述过程以准备这张新表的数据即可。
 
