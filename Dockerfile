FROM python:3.6.4

ENV NODE_VERSION=6

RUN curl -sL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash -

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'

RUN apt-get update && \
  apt-get install -y \
  nodejs unzip \
  # Note that we want postgresql-client so 'manage.py dbshell' works.
  postgresql-client \
  # This is some kind of dependency for headless chrome; See https://crbug.com/795759.
  libgconf-2-4 \
  # Install latest chrome stable package and dependencies.
  # Note that ideally we'd explicitly specify the version of Chrome to use,
  # but there are complications; see https://github.com/18F/calc/issues/1964
  # for more details.
  google-chrome-stable ttf-freefont \
  --no-install-recommends \
  && rm -rf /var/lib/apt/lists/* \
  && rm -rf /src/*.deb

RUN pip install virtualenv

WORKDIR /calc
RUN npm install -g yarn

# Hopefully the latest stable ChromeDriver is compatible with the latest
# stable Chrome. I wish there were more consistently reproducible &
# reliable ways around this, but there don't seem to be; see
# https://github.com/18F/calc/issues/1964 for more details.
RUN wget -N https://chromedriver.storage.googleapis.com/LATEST_RELEASE && \
  wget -N https://chromedriver.storage.googleapis.com/`cat LATEST_RELEASE`/chromedriver_linux64.zip \
  && unzip chromedriver_linux64.zip \
  && chmod +x chromedriver \
  && mv chromedriver /usr/local/bin/chromedriver

ENV PATH /calc/node_modules/.bin:$PATH
ENV DDM_IS_RUNNING_IN_DOCKER yup

ENTRYPOINT ["python", "/calc/docker_django_management.py"]
