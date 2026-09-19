variable "environment" { type = string }
variable "vpc_id" { type = string }
variable "vpc_cidr" { type = string }
variable "subnet_ids" { type = list(string) }
variable "instance_class" { type = string; default = "db.t3.medium" }
variable "db_username" { type = string; default = "unitransit" }
variable "db_password" { type = string; sensitive = true }
