# ===== R8 / ProGuard 规则 =====
# release 开启 minifyEnabled 后生效。原则：只 keep 反射会用到的东西，其余全压。
# 想临时排查崩溃，可把 build.gradle 里的 minifyEnabled 改回 false 重编一版。

# --- Capacitor 核心：Bridge 用反射实例化 Plugin，混淆后找不到类会直接崩 ---
-keep class com.getcapacitor.** { *; }
-keep @com.getcapacitor.annotation.CapacitorPlugin class * { *; }
-keepclassmembers class * {
    @com.getcapacitor.PluginMethod public <methods>;
}
# 插件里暴露给 JS 的方法名不能被改名（JS 是按字符串找它们的）
-keepclassmembers class * {
    @com.getcapacitor.PluginMethod public <methods>;
    @com.getcapacitor.annotation.NativeMethod public *;
}
-keep class com.getcapacitor.plugin.** { *; }

# --- WebView：JS 注入的桥接对象必须保留原名与签名 ---
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}

# --- 本 App 入口 ---
-keep class cn.bigdata.beisai.MainActivity { *; }

# --- androidx ---
-keep class androidx.core.app.** { *; }
-keep class androidx.appcompat.app.** { *; }
-dontwarn androidx.**
-dontwarn org.apache.cordova.**

# --- 保留行号：回溯崩溃堆栈时能看到真实行号 ---
-keepattributes SourceFile,LineNumberTable
-renamesourcefileattribute SourceFile

# --- 压缩期无害告警 ---
-dontwarn java.lang.invoke.**
-dontwarn javax.naming.**
-dontwarn org.slf4j.**
