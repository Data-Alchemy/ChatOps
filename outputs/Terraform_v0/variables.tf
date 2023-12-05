variable "name" {
  description = "The name of the Snowflake instance"
  type        = string
}

variable "vpc_id" {
  description = "The ID of the VPC where the Snowflake instance will be created"
  type        = string
}

variable "subnet_id" {
  description = "The ID of the Subnet where the Snowflake instance will be created"
  type        = string
}

variable "instance_type" {
  description = "The type of instance to start"
  type        = string
}

variable "key_name" {
  description = "The key name to use for the instance"
  type        = string
}

variable "tags" {
  description = "A mapping of tags to assign to the resource"
  type        = map(string)
}