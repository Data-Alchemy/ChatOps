output "snowflake_instance_id" {
  description = "The ID of the Snowflake instance"
  value       = module.snowflake_instance.id
}

output "snowflake_instance_public_ip" {
  description = "The public IP address assigned to the Snowflake instance"
  value       = module.snowflake_instance.public_ip
}

output "snowflake_instance_private_ip" {
  description = "The private IP address assigned to the Snowflake instance"
  value       = module.snowflake_instance.private_ip
}