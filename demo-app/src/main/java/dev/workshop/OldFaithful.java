package dev.workshop;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Map;
import org.apache.commons.text.WordUtils;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

/**
 * A tiny, harmless app. Nothing here is exploited - the point of the workshop is that the code
 * can be perfectly fine while the libraries underneath it are not.
 */
public class OldFaithful {

  private static final Logger LOG = LogManager.getLogger(OldFaithful.class);

  public static void main(String[] args) throws Exception {
    String name = args.length > 0 ? args[0] : "platform engineer";
    String greeting = WordUtils.capitalizeFully("hello, " + name + "!");

    String json = new ObjectMapper().writeValueAsString(Map.of("message", greeting));

    LOG.info("Built greeting {}", json);
    System.out.println(json);
  }
}
