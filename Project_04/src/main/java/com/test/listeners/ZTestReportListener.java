package com.test.listeners;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.test.entity.ReportInfo;
import org.junit.platform.engine.TestExecutionResult;
import org.junit.platform.engine.reporting.ReportEntry;
import org.junit.platform.launcher.TestExecutionListener;
import org.junit.platform.launcher.TestIdentifier;
import org.junit.platform.launcher.TestPlan;

import java.io.*;
import java.text.SimpleDateFormat;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import java.util.regex.Matcher;
import java.util.stream.Stream;

/**
 * @author zhuxuexiang
 * @version 1.0
 * @date 2020/3/29 17:54
 */
public class ZTestReportListener implements TestExecutionListener {
    private final SimpleDateFormat simpleDateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS");
    private String templatePath;
    private long testPlanStartTime;
    private long testPlanFinishTime;
    private TestPlan testPlan;
    private ConcurrentHashMap<String, Long> testIdentifierStartTime = new ConcurrentHashMap<>();
    private ConcurrentHashMap<String, Long> testIdentifierFinishTime = new ConcurrentHashMap<>();
    final AtomicLong containersFound = new AtomicLong();
    final AtomicLong containersStarted = new AtomicLong();
    final AtomicLong containersSkipped = new AtomicLong();
    final AtomicLong containersAborted = new AtomicLong();
    final AtomicLong containersSucceeded = new AtomicLong();
    final AtomicLong containersFailed = new AtomicLong();
    final AtomicLong testsFound = new AtomicLong();
    final AtomicLong testsStarted = new AtomicLong();
    final AtomicLong testsSkipped = new AtomicLong();
    final AtomicLong testsAborted = new AtomicLong();
    final AtomicLong testsSucceeded = new AtomicLong();
    final AtomicLong testsFailed = new AtomicLong();
    private List<ReportInfo> reportInfos = new ArrayList<>();

    public ZTestReportListener(String templatePath) {
        this.templatePath = templatePath;
    }

    public void testPlanExecutionStarted(TestPlan testPlan) {
        this.testPlan = testPlan;
        testPlanStartTime = System.currentTimeMillis();
    }

    public void testPlanExecutionFinished(TestPlan testPlan) {
        testPlanFinishTime = System.currentTimeMillis();
    }

    public void dynamicTestRegistered(TestIdentifier testIdentifier) {
        if (testIdentifier.isContainer()) {
            containersFound.incrementAndGet();
        }

        if (testIdentifier.isTest()) {
            testsFound.incrementAndGet();
        }
    }

    public void executionSkipped(TestIdentifier testIdentifier, String reason) {
        long skippedContainers = Stream.concat(Stream.of(testIdentifier), this.testPlan.getDescendants(testIdentifier).stream()).filter(TestIdentifier::isContainer).count();
        long skippedTests = Stream.concat(Stream.of(testIdentifier), this.testPlan.getDescendants(testIdentifier).stream()).filter(TestIdentifier::isTest).count();
        containersSkipped.addAndGet(skippedContainers);
        testsSkipped.addAndGet(skippedTests);
    }

    public void executionStarted(TestIdentifier testIdentifier) {
        if (testIdentifier.isContainer()) {
            containersStarted.incrementAndGet();
        }

        if (testIdentifier.isTest()) {
            testsStarted.incrementAndGet();
        }
        testIdentifierStartTime.put(testIdentifier.getUniqueId(), System.currentTimeMillis());
    }

    public void executionFinished(TestIdentifier testIdentifier, TestExecutionResult testExecutionResult) {
        String uniqueId = testIdentifier.getUniqueId();
        TestExecutionResult.Status status = testExecutionResult.getStatus();

        testIdentifierFinishTime.put(uniqueId, System.currentTimeMillis());

        switch (status) {
            case SUCCESSFUL:
                if (testIdentifier.isContainer()) {
                    containersSucceeded.incrementAndGet();
                }

                if (testIdentifier.isTest()) {
                    testsSucceeded.incrementAndGet();
                }
                break;
            case ABORTED:
                if (testIdentifier.isContainer()) {
                    containersAborted.incrementAndGet();
                }

                if (testIdentifier.isTest()) {
                    testsAborted.incrementAndGet();
                }
                break;
            default:
                if (testIdentifier.isContainer()) {
                    containersFailed.incrementAndGet();
                }

                if (testIdentifier.isTest()) {
                    testsFailed.incrementAndGet();
                }
        }

        if (testIdentifier.isTest()) {
            addReportInfo(testIdentifier, testExecutionResult);
        }
    }

    /**
     * 已经执行的测试方法加到报告上
     *
     * @param testIdentifier
     * @param testExecutionResult
     */
    private void addReportInfo(TestIdentifier testIdentifier, TestExecutionResult testExecutionResult) {
        ReportInfo info = new ReportInfo();
        String uniqueId = testIdentifier.getUniqueId();
        String displayName = testIdentifier.getDisplayName();
        Long startTime = testIdentifierStartTime.get(uniqueId);
        Long finishTime = testIdentifierFinishTime.get(uniqueId);
        long spendTime = finishTime - startTime;
        String statusDesc = this.getStatus(testExecutionResult.getStatus());
        List<String> logs = new ArrayList<>();

        Optional<Throwable> optionalThrowable = testExecutionResult.getThrowable();
        if (optionalThrowable.isPresent()) {
            Throwable throwable = optionalThrowable.get();
            logs.add(this.toHtml(throwable.toString()));
            StackTraceElement[] st = throwable.getStackTrace();
            for (StackTraceElement stackTraceElement : st) {
                logs.add(this.toHtml("    " + stackTraceElement));
            }
        }

        info.setName(displayName);
        info.setSpendTime(spendTime + "ms");
        info.setStatus(statusDesc);
        info.setClassName(testIdentifier.getLegacyReportingName());
        info.setMethodName(testIdentifier.getLegacyReportingName());
        info.setDescription(testIdentifier.getLegacyReportingName());
        info.setLog(logs);

        reportInfos.add(info);
    }

    @Override
    public void reportingEntryPublished(TestIdentifier testIdentifier, ReportEntry entry) {

    }

    /**
     * 输出report.html
     *
     * @param reporterDir html报告所在的目录
     */
    public void outputResult(String reporterDir) {
        try {
            File file = new File(reporterDir);
            if (!file.exists()) {
                file.mkdirs();
            }
            String destPath = reporterDir + File.separator + "report.html";

            String testPlanBeginTime = simpleDateFormat.format(testPlanStartTime);
            Map<String, Object> result = new HashMap<String, Object>();
            result.put("testName", testPlan.getClass().getCanonicalName());
            result.put("testPass", testsSucceeded.get());
            result.put("testFail", testsFailed.get());
            result.put("testSkip", testsSkipped.get());
            result.put("testAll", testsStarted);
            result.put("beginTime", testPlanBeginTime);
            result.put("totalTime", (testPlanFinishTime - testPlanStartTime) + "ms");
            result.put("testResult", reportInfos);
            Gson gson = new GsonBuilder().disableHtmlEscaping().setPrettyPrinting().create();
            if (templatePath == null) {
                throw new Exception("template path can not be null");
            }
            String template = this.read(templatePath);
            BufferedWriter output = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(new File(destPath)), "UTF-8"));
            String jsonString = gson.toJson(result);
            template = template.replaceFirst("\\$\\{resultData\\}", Matcher.quoteReplacement(jsonString));
            output.write(template);
            output.flush();
            output.close();
        } catch (Exception e) {
            e.printStackTrace();
        }

    }

    private String getStatus(TestExecutionResult.Status status) {
        String statusString = null;
        switch (status) {
            case SUCCESSFUL:
                statusString = "成功";
                break;
            case FAILED:
                statusString = "失败";
                break;
            case ABORTED:
                statusString = "跳过";
                break;
        }
        return statusString;
    }

    private String toHtml(String str) {
        if (str == null) {
            return "";
        } else {
            str = str.replaceAll("<", "&lt;");
            str = str.replaceAll(">", "&gt;");
            str = str.replaceAll(" ", "&nbsp;");
            str = str.replaceAll("\n", "<br>");
            str = str.replaceAll("\"", "\\\\\"");
        }
        return str;
    }

    private String read(String path) {
        File file = new File(path);
        InputStream is = null;
        StringBuffer sb = new StringBuffer();
        try {
            is = new FileInputStream(file);
            int index = 0;
            byte[] b = new byte[1024];
            while ((index = is.read(b)) != -1) {
                sb.append(new String(b, 0, index));
            }
            return sb.toString();
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            try {
                if (is != null) {
                    is.close();
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
        return null;
    }
}
