./build.sh && ./install.sh && /usr/sbin/semodule -s targeted -i /usr/share/selinux/targeted/pulp-server.pp && ./dev_setup_label.sh && ./relabel.sh
