# Timestream 压测工具及方法


1. 打开 AWS console，在您希望的目标区域创建 timestream 以及 kinesis。 注：Timestream目前并未在所有的 AWS 区域上线，所有上线的区域请查看[此页面](https://aws.amazon.com/cn/timestream/pricing/),本文用的是 N.Virginia (us-east-1)区域.
1. 在 Timestream 当中创建一个数据库，名为 ``kdaflink`` 。[点击查看创建方法](https://docs.aws.amazon.com/zh_cn/timestream/latest/developerguide/console_timestream.html#console_timestream.db.using-console)
1. 创建一个 table 名为 ``kinesisdata1``。[点击查看创建方法](https://docs.aws.amazon.com/zh_cn/timestream/latest/developerguide/console_timestream.html#console_timestream.table.using-console)
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
 