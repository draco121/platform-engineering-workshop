package {{ cookiecutter.package_name }}.api;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/** Example endpoint. Delete it once you add your own - everything around it stays. */
@RestController
public class GreetingController {

  private static final Logger log = LoggerFactory.getLogger(GreetingController.class);

  public record Greeting(String message, String service) {}

  @GetMapping("/api/greeting")
  public Greeting greet(
      @RequestParam(defaultValue = "world") @NotBlank @Size(max = 40) String name) {
    log.info("Greeting requested for {}", name);
    return new Greeting("Hello, " + name + "!", "{{ cookiecutter.service_slug }}");
  }
}
