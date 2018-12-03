FROM robbyjo/ubuntu-mkl:16.04-2018.1

MAINTAINER Trevor Morton

# Install some dependencies
RUN apt-get update && apt-get install -y \
		bc \
		build-essential \
		cmake \
		curl \
		g++ \
		git \
		nano \
		pkg-config \
		software-properties-common \
		unzip \
		vim \
		ant \
		python3-pip \
		openjdk-8-jdk \
		doxygen \
		xvfb \
		maven \
		language-pack-en \
		language-pack-en-base \
		wmctrl \
		&& \
	apt-get clean && \
	apt-get autoremove && \
	rm -rf /var/lib/apt/lists/*

RUN apt-add-repository ppa:dolphin-emu/ppa -y && apt update && apt install -y dolphin-emu

# Install other useful Python packages using pip
RUN pip3 --no-cache-dir install --upgrade ipython && \
	pip3 --no-cache-dir install \
		Cython \
		numpy \
		Pillow \
		wheel \ 
		python-xlib \
		mss \
		opencv-python

# Download, build, and install jpy
RUN export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64 && \
	export JDK_HOME=/usr/lib/jvm/java-8-openjdk-amd64 && \
	cd /home && \
	git clone https://github.com/bcdev/jpy.git && \
	cd jpy && \
	python3 setup.py --maven bdist_wheel && \
	mvn install:install-file -Dfile=build/lib.linux-x86_64-3.5/jpy-0.10.0-SNAPSHOT.jar -DpomFile=pom.xml

# Download and install MasBot
RUN cd /home && \
	git clone https://github.com/TrevorCMorton/MasBot.git && \
	cd MasBot && \
	git checkout dev && \
	mvn install

# Download and build Runners
RUN cd /home && \
	git clone https://github.com/TrevorCMorton/Runners.git && \
	cd Runners && \
	mvn package

# Make named pipes in dolphin config folder
RUN cd /home/Runners/.dolphin-emu/MemoryWatcher && \
	mkfifo MemoryWatcher && \
	cd .. && \
	mkdir Pipes && \
	cd Pipes && \
	mkfifo p3

# Include the game iso
ADD Melee.iso /home/Runners

WORKDIR "/root"
CMD (Xvfb :5 -screen 0 1920x1080x24 &) && \
	export DISPLAY=:5 && \
	cd /home/Runners && \
	timeout 600s java -jar target/Runners-1.0-SNAPSHOT-bin.jar $PROB true jpyconfig.propertiesfile true
	
