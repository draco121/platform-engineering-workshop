package {{ cookiecutter.package_name }};

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/** {{ cookiecutter.service_name }}: {{ cookiecutter.description }} */
@SpringBootApplication
public class Application {

  public static void main(String[] args) {
    SpringApplication.run(Application.class, args);
  }
}
