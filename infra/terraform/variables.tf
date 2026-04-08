variable "aws_region" {
  default = "us-west-1"
}

variable "instance_type" {
  default = "t3.micro"
}

variable "key_name" {
  description = "SSH key pair name"
}

variable "allowed_ip" {
  description = "Your IP for admin access"
}