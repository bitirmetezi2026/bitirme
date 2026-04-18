import java.util.Properties
import java.io.FileInputStream

plugins {
    alias(libs.plugins.android.application)
    // libs.versions.toml'da ismini "jetbrains-kotlin-android" yaptık, o yüzden burası böyle olmalı:
    alias(libs.plugins.jetbrains.kotlin.android)
    // Kotlin 2.0 için bu plugin şart:
    alias(libs.plugins.compose.compiler)
}

android {
    namespace = "com.example.caloriecalculator"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.example.caloriecalculator"
        minSdk = 24
        targetSdk = 36
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables {
            useSupportLibrary = true
        }

        val envFile = rootProject.file(".env")
        val envProps = Properties()
        if (envFile.exists()) {
            envProps.load(FileInputStream(envFile))
        }
        buildConfigField("String", "DILA_BACKEND_URL", "\"${envProps.getProperty("DILA_BACKEND_URL", "http://192.168.1.12:8000/")}\"")
        buildConfigField("String", "MEMET_AI_URL", "\"${envProps.getProperty("MEMET_AI_URL", "http://192.168.1.11:8000/")}\"")
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }
    kotlinOptions {
        jvmTarget = "1.8"
    }
    buildFeatures {
        compose = true
        buildConfig = true
    }
    composeOptions {
        // Kotlin 2.0 kullandığımız için burası BOŞ kalmalı.
        // Versiyonu plugin otomatik ayarlıyor.
    }
    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}

dependencies {

    // --- TEMEL KÜTÜPHANELER ---
    implementation(libs.androidx.core.ktx)
    implementation("androidx.appcompat:appcompat:1.7.0")
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.activity.compose)
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.ui)
    implementation(libs.androidx.ui.graphics)
    implementation(libs.androidx.ui.tooling.preview)
    implementation(libs.androidx.material3)
    implementation("androidx.compose.material:material-icons-extended:1.6.7")
    // --- EKLENEN KÜTÜPHANELER (Chatbot ve Tasarım İçin) ---

    // İkonlar (Send, Chat vb. ikonlar için)
    implementation(libs.androidx.material.icons.extended)

    // Navigasyon (Sayfalar arası geçiş için)
    implementation(libs.androidx.navigation.compose)

    // Splash Screen (Açılış ekranı için)
    implementation(libs.androidx.core.splashscreen)

    // --- NETWORK (API Bağlantısı İçin) ---
    implementation(libs.retrofit)
    implementation(libs.converter.gson)
    implementation(libs.kotlinx.coroutines.android)

    // --- TEST ---
    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.junit)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(platform(libs.androidx.compose.bom))
    androidTestImplementation(libs.androidx.ui.test.junit4)
    debugImplementation(libs.androidx.ui.tooling)
    debugImplementation(libs.androidx.ui.test.manifest)

    // OkHttp kütüphaneleri
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    // Resim yükleme kütüphanesi
    implementation("io.coil-kt:coil-compose:2.6.0")
    // TensorFlow Lite kütüphaneleri
    implementation("org.tensorflow:tensorflow-lite:2.16.1")
    implementation("org.tensorflow:tensorflow-lite-support:0.4.4")
}
