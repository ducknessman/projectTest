import com.test.listeners.ZTestReportListener;
import com.testcase.TestDemo1;
import org.junit.platform.launcher.Launcher;
import org.junit.platform.launcher.LauncherDiscoveryRequest;
import org.junit.platform.launcher.core.LauncherDiscoveryRequestBuilder;
import org.junit.platform.launcher.core.LauncherFactory;

import static org.junit.platform.engine.discovery.DiscoverySelectors.selectClass;

/**
 * @author zhuxuexiang
 * @version 1.0
 * @date 2020/3/29 17:54
 */
public class TestPlanExample {
    public static void main(String[] args) {
        try {
            LauncherDiscoveryRequest request = LauncherDiscoveryRequestBuilder
                    .request()
                    .selectors(selectClass(TestDemo1.class))
                    .build();
            Launcher launcher = LauncherFactory.create();

            // 注册执行结果监听器
            // html测试报告生成
            ZTestReportListener listener = new ZTestReportListener("D:\\java_project\\junitHtmlReport-master\\src\\main\\resources\\report.template");
            launcher.registerTestExecutionListeners(listener);
            launcher.execute(request);
            listener.outputResult("D:\\java_project\\junitHtmlReport-master\\report");
            // 报告看情况入库还是直接展示

        } catch (Exception e) {
            e.printStackTrace();
        } finally {
        }
    }

}
