#
# Cookbook Name:: mysql-mha
# Attributes:: manager
#

# MHA manager package related
default["mysql_mha"]["manager"]["version"]      = "0.56-0.el6"
default["mysql_mha"]["manager"]["package_name"] = "mha4mysql-manager-#{node["mysql_mha"]["manager"]["version"]}.noarch.rpm"
default["mysql_mha"]["manager"]["source"]       = "https://72003f4c60f5cc941cd1c7d448fc3c99e0aebaa8.googledrive.com/host/0B1lu97m8-haWeHdGWXp0YVVUSlk/#{node["mysql_mha"]["manager"]["package_name"]}"
default["mysql_mha"]["manager"]["checksum"]     = "0f137d9d14ac8f6dc82fd73fad67484e5d5b6bc38cef5eb9269056ac19ff7df8"