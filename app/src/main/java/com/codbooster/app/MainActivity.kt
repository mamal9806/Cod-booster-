package com.codbooster.app

import android.app.ActivityManager
import android.content.Context
import android.content.Intent
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.os.BatteryManager
import android.os.Build
import android.os.Bundle
import android.os.PowerManager
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.animateContentSize
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInVertically
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext
import java.net.HttpURLConnection
import java.net.URL

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { BoosterScreen(this) }
    }
}

private data class DeviceStats(
    val device: String,
    val android: String,
    val chipset: String,
    val ramFree: String,
    val ramTotal: String,
    val batteryTemp: String,
    val thermal: String,
    val network: String,
    val ping: String,
    val gameInstalled: Boolean
)

private fun readStats(context: Context, ping: String = "در حال بررسی…"): DeviceStats {
    val am = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
    val mem = ActivityManager.MemoryInfo()
    am.getMemoryInfo(mem)
    val total = mem.totalMem / 1024 / 1024
    val free = mem.availMem / 1024 / 1024

    val battery = context.registerReceiver(null, IntentFilterCompat.batteryChanged())
    val temp = battery?.getIntExtra(BatteryManager.EXTRA_TEMPERATURE, -1) ?: -1
    val tempText = if (temp > 0) String.format("%.1f°C", temp / 10f) else "نامشخص"

    val pm = context.getSystemService(Context.POWER_SERVICE) as PowerManager
    val thermalText = if (Build.VERSION.SDK_INT >= 29) {
        when (pm.currentThermalStatus) {
            PowerManager.THERMAL_STATUS_NONE -> "عادی"
            PowerManager.THERMAL_STATUS_LIGHT -> "کمی گرم"
            PowerManager.THERMAL_STATUS_MODERATE -> "گرم"
            PowerManager.THERMAL_STATUS_SEVERE -> "داغ"
            PowerManager.THERMAL_STATUS_CRITICAL -> "بسیار داغ"
            else -> "نامشخص"
        }
    } else "در دسترس نیست"

    val cm = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
    val caps = cm.getNetworkCapabilities(cm.activeNetwork)
    val network = when {
        caps == null -> "قطع"
        caps.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) -> "داده سیم‌کارت"
        caps.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) -> "Wi‑Fi"
        else -> "متصل"
    }

    val packages = listOf("com.activision.callofduty.shooter", "com.garena.game.codm")
    val installed = packages.any { p ->
        try { context.packageManager.getPackageInfo(p, 0); true } catch (_: Exception) { false }
    }

    return DeviceStats(
        "${Build.MANUFACTURER} ${Build.MODEL}",
        "Android ${Build.VERSION.RELEASE} (API ${Build.VERSION.SDK_INT})",
        "${Build.HARDWARE} / ${Build.SUPPORTED_ABIS.firstOrNull().orEmpty()}",
        "${free} MB", "${total} MB", tempText, thermalText, network, ping, installed
    )
}

private object IntentFilterCompat {
    fun batteryChanged() = android.content.IntentFilter(Intent.ACTION_BATTERY_CHANGED)
}

private suspend fun measureLatency(): String = withContext(Dispatchers.IO) {
    try {
        val start = System.nanoTime()
        val conn = (URL("https://www.google.com/generate_204").openConnection() as HttpURLConnection)
        conn.connectTimeout = 3500
        conn.readTimeout = 3500
        conn.requestMethod = "GET"
        conn.instanceFollowRedirects = false
        conn.connect()
        val code = conn.responseCode
        conn.disconnect()
        val ms = (System.nanoTime() - start) / 1_000_000
        if (code in 200..399) "${ms} ms*" else "نامشخص"
    } catch (_: Exception) { "نامشخص" }
}

@Composable
private fun BoosterScreen(context: Context) {
    val scope = rememberCoroutineScope()
    var stats by remember { mutableStateOf(readStats(context)) }
    var scanning by remember { mutableStateOf(false) }
    var boostMessage by remember { mutableStateOf("آماده برای بررسی دستگاه") }

    val bg = Color(0xFF080B14)
    val panel = Color(0xFF151B2B)
    val cyan = Color(0xFF79E7FF)
    val muted = Color.White

    MaterialTheme(colorScheme = darkColorScheme(
        background = bg, surface = panel, primary = cyan,
        onBackground = Color.White, onSurface = Color.White
    )) {
        Column(
            Modifier.fillMaxSize().background(
                Brush.verticalGradient(listOf(Color(0xFF101B31), bg, Color(0xFF080B14)))
            ).verticalScroll(rememberScrollState()).padding(18.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(Modifier.size(46.dp).clip(RoundedCornerShape(16.dp))
                    .background(Brush.linearGradient(listOf(cyan, Color(0xFF6677FF)))).alpha(pulse),
                    contentAlignment = Alignment.Center) {
                    Icon(Icons.Default.Bolt, null, tint = Color(0xFF07101D), modifier = Modifier.size(28.dp))
                }
                Spacer(Modifier.width(12.dp))
                Column(Modifier.weight(1f)) {
                    Text("COD BOOSTER", fontSize = 21.sp, fontWeight = FontWeight.Black, color = Color.White)
                    Text("SMART GAMING ASSISTANT", fontSize = 10.sp, color = Color.White, letterSpacing = 2.sp)
                }
                Surface(shape = CircleShape, color = Color(0xFF173D3B)) {
                    Text("NO ROOT", Modifier.padding(horizontal = 11.dp, vertical = 7.dp),
                        color = Color(0xFF7EF0C1), fontSize = 10.sp, fontWeight = FontWeight.Bold)
                }
            }

            GlassCard(panel) {
                Text("وضعیت دستگاه", color = muted, fontSize = 13.sp)
                Text(stats.device, fontSize = 19.sp, fontWeight = FontWeight.Bold)
                Text("${stats.android}  •  ${stats.chipset}", color = muted, fontSize = 11.sp)
                Spacer(Modifier.height(8.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Metric("RAM آزاد", stats.ramFree, Icons.Default.Memory, cyan, Modifier.weight(1f))
                    Metric("دمای باتری", stats.batteryTemp, Icons.Default.Thermostat, Color(0xFFFFC078), Modifier.weight(1f))
                }
                Spacer(Modifier.height(8.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Metric("وضعیت حرارتی", stats.thermal, Icons.Default.DeviceThermostat, Color(0xFFB8A1FF), Modifier.weight(1f))
                    Metric("اتصال", stats.network, Icons.Default.NetworkCheck, Color(0xFF7EF0C1), Modifier.weight(1f))
                }
            }

            GlassCard(panel) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Column(Modifier.weight(1f)) {
                        Text("آماده‌سازی هوشمند", fontSize = 17.sp, fontWeight = FontWeight.Bold)
                        Text("بررسی منابع و وضعیت اتصال", color = muted, fontSize = 12.sp)
                    }
                    Icon(Icons.Default.AutoAwesome, null, tint = cyan, modifier = Modifier.size(26.dp))
                }
                Spacer(Modifier.height(12.dp))
                Button(
                    onClick = {
                        scanning = true
                        boostMessage = "در حال بررسی وضعیت دستگاه و شبکه…"
                        scope.launch {
                            val latency = measureLatency()
                            stats = readStats(context, latency)
                            scanning = false
                            boostMessage = "بررسی انجام شد؛ پیشنهادها بر اساس وضعیت فعلی آماده‌اند."
                        }
                    },
                    enabled = !scanning,
                    modifier = Modifier.fillMaxWidth().height(54.dp),
                    shape = RoundedCornerShape(18.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = cyan, contentColor = Color(0xFF07101D))
                ) {
                    if (scanning) CircularProgressIndicator(Modifier.size(20.dp), strokeWidth = 2.dp)
                    else Icon(Icons.Default.Bolt, null)
                    Spacer(Modifier.width(8.dp))
                    Text(if (scanning) "در حال اسکن…" else "SMART BOOST", fontWeight = FontWeight.Black)
                }
                Text(boostMessage, color = muted, fontSize = 12.sp)
                Text("پینگ تقریبی اینترنت: ${stats.ping}", color = cyan, fontSize = 13.sp)
                Text("* این عدد تأخیر تا سرویس آزمایشی اینترنت است، نه پینگ سرور کالاف.", color = muted, fontSize = 10.sp)
            }

            GlassCard(panel) {
                Text("وضعیت Call of Duty Mobile", fontSize = 17.sp, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(6.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(if (stats.gameInstalled) Icons.Default.CheckCircle else Icons.Default.Info,
                        null, tint = if (stats.gameInstalled) Color(0xFF7EF0C1) else Color(0xFFFFC078))
                    Spacer(Modifier.width(8.dp))
                    Text(if (stats.gameInstalled) "بازی شناسایی شد" else "بازی در فهرست برنامه‌های قابل‌شناسایی پیدا نشد",
                        color = muted, fontSize = 12.sp)
                }
                Spacer(Modifier.height(10.dp))
                OutlinedButton(
                    onClick = { launchCod(context) },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(15.dp)
                ) {
                    Icon(Icons.Default.SportsEsports, null)
                    Spacer(Modifier.width(8.dp))
                    Text("اجرای Call of Duty Mobile")
                }
            }

            GlassCard(panel) {
                Text("پیشنهادهای بهینه‌سازی", fontSize = 17.sp, fontWeight = FontWeight.Bold)
                Tip("گرافیک بازی", "برای اولویت FPS، گرافیک را روی Low و نرخ فریم را روی بالاترین گزینه پایدار قرار بده.")
                Tip("دما", "هنگام شارژ بازی نکن و اگر گوشی داغ شد، چند دقیقه به آن استراحت بده.")
                Tip("شبکه", "در محل دارای آنتن‌دهی بهتر بازی کن؛ VPN و دانلودهای پس‌زمینه می‌توانند تأخیر را بیشتر کنند.")
            }

            Text("نسخه 0.2.0 • ابزار کمکی بدون روت", color = muted, fontSize = 10.sp,
                modifier = Modifier.align(Alignment.CenterHorizontally))
        }
    }
}

private fun launchCod(context: Context) {
    val candidates = listOf("com.activision.callofduty.shooter", "com.garena.game.codm")
    for (pkg in candidates) {
        val intent = context.packageManager.getLaunchIntentForPackage(pkg)
        if (intent != null) {
            context.startActivity(intent)
            return
        }
    }
}

@Composable
private fun GlassCard(color: Color, content: @Composable ColumnScope.() -> Unit) {
    Surface(
        color = color.copy(alpha = 0.78f),
        shape = RoundedCornerShape(26.dp),
        modifier = Modifier.fillMaxWidth().border(1.dp, Color.White.copy(alpha = 0.10f), RoundedCornerShape(26.dp)),
        tonalElevation = 4.dp
    ) {
        Column(Modifier.padding(17.dp).animateContentSize(), verticalArrangement = Arrangement.spacedBy(7.dp), content = content)
    }
}

@Composable
private fun Metric(label: String, value: String, icon: ImageVector, tint: Color, modifier: Modifier = Modifier) {
    Surface(modifier = modifier, color = Color.White.copy(alpha = 0.045f), shape = RoundedCornerShape(17.dp)) {
        Column(Modifier.padding(12.dp)) {
            Icon(icon, null, tint = tint, modifier = Modifier.size(19.dp))
            Spacer(Modifier.height(5.dp))
            Text(value, fontSize = 15.sp, fontWeight = FontWeight.Bold)
            Text(label, fontSize = 10.sp, color = Color.White)
        }
    }
}

@Composable
private fun Tip(title: String, body: String) {
    Row(Modifier.padding(top = 5.dp), verticalAlignment = Alignment.Top) {
        Icon(Icons.Default.CheckCircle, null, tint = Color(0xFF79E7FF), modifier = Modifier.size(17.dp))
        Spacer(Modifier.width(8.dp))
        Column {
            Text(title, fontWeight = FontWeight.SemiBold, fontSize = 13.sp)
            Text(body, color = Color(0xFFAAB5C9), fontSize = 11.sp)
        }
    }
}
