---
title: "Logging information"
---

# Logging information

There are currently two loggers that are being used in the code:

  * LOG is a logger that can be used to log both info and error messages (LOG.info(), LOG.error())
  * LOG_ERROR is a logger that is used only for error messages. (LOG_ERROR.error())



Both of these loggers send their messages to both Graylog and Sentry.  
The difference is that there is a filter in Sentry that accepts only error messages. So messages LOG.info() will not appear there.

It should also be noted that Sentry stores logs for up to three months, while Graylog only stores them for seven days.

**LOG should be selected instead of LOG_ERROR, because the LOG logger holds information of the file where the log exists.**

## Verification notes

The page's description of `LOG` and `LOG_ERROR` is partially confirmed by the source code. The following observations were identified.

**`LOG_ERROR` confirmed.** The logger name `error_logger` and the pattern of defining `LOG_ERROR = LoggerFactory.getLogger("error_logger")` are confirmed by multiple Java source files, for example `RestoreDataCollectionSnapshotCommand.java`, `ReferenceDatasetSnapshotCommand.java`, and `SaveStatisticsCommand.java` in `dataset-service`. The claim that `LOG_ERROR` routes only to `stderr` is confirmed by the `logback.xml` files, which define the `error_logger` logger with only a `stderr` appender.

**Sentry integration confirmed.** All `logback.xml` files inspected (`api-gateway`, `dataset-service`, `validation-service`, and others) include an `io.sentry.logback.SentryAppender` with a `ThresholdFilter` at `ERROR` level, confirming that error-level log messages are forwarded to Sentry and that `INFO`-level messages are not.

**Graylog claim cannot be confirmed.** The page states "both of these loggers send their messages to both Graylog and Sentry." No `logback.xml` file in the source tree contains a Graylog or GELF appender. Every `logback.xml` examined routes to `stdout`, `stderr`, and Sentry only. Graylog likely collects logs by scraping container stdout/stderr from the Kubernetes node (the standard approach for Graylog in a container environment), which would explain why there is no in-process GELF appender — but the page implies a direct logger-to-Graylog connection that does not exist at the application level.

**Storage retention figures.** The page states "Sentry stores logs for up to three months, while Graylog only stores them for seven days." These are operational configuration values that cannot be verified from the service source code. They are plausible defaults but may not reflect the current EEA instance configuration.

**Recommendation about `LOG` vs `LOG_ERROR`.** The recommendation that `LOG` should be preferred over `LOG_ERROR` is consistent with the source code convention: `LOG_ERROR` appears only in a small number of specific command handlers, while `LOG` is the standard logger throughout the codebase.
