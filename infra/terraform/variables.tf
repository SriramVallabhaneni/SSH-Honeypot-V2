variable "aws_region" {
}

variable "instance_type" {
}

variable "key_name" {
  description = "SSH key pair name"
}

variable "allowed_ip" {
  description = "Your IP for admin access"
}

variable "repo_url" {
  description = "Public GitHub repository URL"
}

variable "app_dir" {
  description = "Directory on the EC2 instance where the app will live"
  default     = "/opt/ssh-honeypot-v2"
}

variable "postgres_password" {
  description = "Password for the internal Postgres container"
  sensitive   = true
}