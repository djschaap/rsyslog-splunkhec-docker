# rsyslog-splunkhec-docker

Docker image for running rsyslog & omsplunkhec within Docker.

Based on Alpine Linux.

USE AT YOUR OWN RISK.

Project Home: https://github.com/djschaap/rsyslog-splunkhec-docker

Docker Hub: https://cloud.docker.com/repository/docker/djschaap/rsyslog-splunkhec-docker

## Makefile targets

- Makefile from https://github.com/mvanholsteijn/docker-makefile

```
make patch-release	increments the patch release level, build and push to registry
make minor-release	increments the minor release level, build and push to registry
make major-release	increments the major release level, build and push to registry
make release		build the current release and push the image to the registry
make build		builds a new version of your Docker image and tags it
make snapshot		build from the current (dirty) workspace and pushes the image to the registry
make check-status	will check whether there are outstanding changes
make check-release	will check whether the current directory matches the tagged release in git.
make showver		will show the current release tag based on the directory content.
make shell		build, then start container and run /bin/ash
make test		build, then start container and run tests
```

## liblognorm Tests

make test

or, within container: python -m unittest discover

## See Also

- https://github.com/rsyslog/rsyslog-docker
- https://bitbucket.org/rfaircloth-splunk/rsyslog-omsplunk/src
- https://github.com/mvanholsteijn/docker-makefile
