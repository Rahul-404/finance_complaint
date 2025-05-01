### [2025-05-01] Installing Java
- Problem: setting java path in home brew manager in macOS
- Tried: setting the path using terminal
- Solution:
    - brew install openjdk@11
    - sudo ln -sfn /opt/homebrew/opt/openjdk@11/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk-11.jdk
    - Set environment variables: Add this to your ~/.zshrc or ~/.bash_profile.
    - 1. open terminal type this command: `/usr/libexec/java_home -V`, it will give use path and version
    - 2. type `pwd` , will get our present working directory
    - 3. now type `ls -al`, will get list of files + hidden directories there we can locate `.zshrc` or `.bash_profile` if they are not there we have to create those
    - 4. now open it to edit, `open .zshrc`
    - 5. copy paste this to it ` # Set Java 11 for PySpark
                                export JAVA_HOME="/opt/homebrew/opt/openjdk@11"
                                export PATH="$JAVA_HOME/bin:$PATH"`
        and save it, if trouble while saving, try this `sudo chown $USER ~/.zshrc` this will shift the owner ship to you.
    - 6. finally do this `source ~/.zshrc` 
- Status: Unresolved

### [2025-05-01] PySpark Execution Issue : Failed to initialize Spark session
- Problem: java.net.BindException: Can't assign requested address: Service 'sparkDriver' failed after 16 retries (on a random free port)! Consider explicitly setting the appropriate binding address for the service 'sparkDriver' (for example spark.driver.bindAddress for SparkDriver) to the correct binding address.
- Tried: Uninstalling - installing pyspark
- Solution: 1. Reinstalled JAVA and PySpark
            2. set environment variable in `.bash_prfile` file rather than `.zshrc` file
- Status: Resolved