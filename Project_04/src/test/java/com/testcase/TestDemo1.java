package com.testcase;

import org.junit.Assert;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.lang.reflect.Method;

public class TestDemo1 {

    @BeforeEach
    public void beforeMethod(Method m) {
        if ("testDemo3".equals(m.getName())) {
            int a = 1 / 0;
            System.out.println(a);
        }
    }

    @Test
    public void testDemo() {
        int a = 1 / 0;
        System.out.println(a);
        Assert.assertEquals("a", "b", "should be equals.");
    }

    @Test
    public void testDemo1() {
        Assert.assertEquals("should be equals.", "a", "b");
    }

    @Test
    public void testDemo2() {
        Assert.assertEquals("should be equals.", 1, 1);
    }

    @Test
    public void testDemo3() {
        Assert.assertEquals("should be equals.", "a", "a");
    }

}
