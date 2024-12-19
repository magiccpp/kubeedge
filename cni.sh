function install_cni_plugins() {
  CNI_DOWNLOAD_ADDR=${CNI_DOWNLOAD_ADDR:-"https://github.com/containernetworking/plugins/releases/download/v1.1.1/cni-plugins-linux-arm64-v1.1.1.tgz"}
  CNI_PKG=${CNI_DOWNLOAD_ADDR##*/}
  CNI_CONF_OVERWRITE=${CNI_CONF_OVERWRITE:-"true"}
  echo -e "The installation of the cni plugin will overwrite the cni config file. Use export CNI_CONF_OVERWRITE=false to disable it."

  # install CNI plugins if not exist
  if [ ! -f "/opt/cni/bin/loopback" ]; then
    echo -e "start installing CNI plugins..."
    sudo mkdir -p /opt/cni/bin
    wget ${CNI_DOWNLOAD_ADDR}
    if [ ! -f ${CNI_PKG} ]; then
      echo -e "cni plugins package does not exits"
      exit 1
    fi
    sudo tar Cxzvf /opt/cni/bin ${CNI_PKG}
    sudo rm -rf ${CNI_PKG}
    if [ ! -f "/opt/cni/bin/loopback" ]; then
      echo -e "the ${CNI_PKG} package does not contain a loopback file."
      exit 1
    fi

    # create CNI netconf file
    CNI_CONFIG_FILE="/etc/cni/net.d/10-containerd-net.conflist"
    if [ -f ${CNI_CONFIG_FILE} ]; then
      if [ ${CNI_CONF_OVERWRITE} == "false" ]; then
        echo -e "CNI netconf file already exist and will no overwrite"
        return
      fi
      echo -e "Configuring cni, ${CNI_CONFIG_FILE} already exists, will be backup as ${CNI_CONFIG_FILE}-bak ..."
      sudo mv ${CNI_CONFIG_FILE} ${CNI_CONFIG_FILE}-bak
    fi
    sudo mkdir -p "/etc/cni/net.d/"
    sudo sh -c 'cat > '${CNI_CONFIG_FILE}' <<EOF
{
  "cniVersion": "1.0.0",
  "name": "containerd-net",
  "plugins": [
    {
      "type": "bridge",
      "bridge": "cni0",
      "isGateway": true,
      "ipMasq": true,
      "promiscMode": true,
      "ipam": {
        "type": "host-local",
        "ranges": [
          [{
            "subnet": "10.88.0.0/16"
          }],
          [{
            "subnet": "2001:db8:4860::/64"
          }]
        ],
        "routes": [
          { "dst": "0.0.0.0/0" },
          { "dst": "::/0" }
        ]
      }
    },
    {
      "type": "portmap",
      "capabilities": {"portMappings": true}
    }
  ]
}
EOF'
  else
    echo "CNI plugins already installed and no need to install"
  fi
}

install_cni_plugins

