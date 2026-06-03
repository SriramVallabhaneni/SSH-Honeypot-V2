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

variable "root_volume_size" {
  description = "Root EBS volume size in GiB. Kubernetes plus monitoring needs more than a tiny root disk."
  type        = number
  default     = 20
}