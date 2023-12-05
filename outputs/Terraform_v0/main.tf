module "snowflake_instance" {
  source  = "SnowflakeDev/snowflake/aws"
  version = "1.0.0"

  name = "my-snowflake-instance"

  vpc_id = "vpc-abcde012"
  subnet_id = "subnet-abcde012"

  instance_type = "m5.large"
  key_name = "my-key-pair"

  tags = {
    Name = "my-snowflake-instance"
    Environment = "test"
  }
}