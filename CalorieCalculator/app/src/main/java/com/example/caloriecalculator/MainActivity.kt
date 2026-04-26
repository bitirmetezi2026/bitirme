package com.example.caloriecalculator

import android.graphics.Bitmap
import android.net.Uri
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.PickVisualMediaRequest
import androidx.activity.result.contract.ActivityResultContracts
import androidx.annotation.DrawableRes
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.Chat
import androidx.compose.material.icons.automirrored.filled.ArrowForwardIos
import androidx.compose.material.icons.automirrored.filled.Send
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.MonitorHeart
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.appcompat.app.AppCompatDelegate
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import androidx.navigation.NavController
import androidx.navigation.NavGraphBuilder
import androidx.navigation.compose.*
import com.example.caloriecalculator.ui.theme.*
import okhttp3.MultipartBody
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.RequestBody.Companion.toRequestBody
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        installSplashScreen()
        enableEdgeToEdge()
        super.onCreate(savedInstanceState)
        setContent {
            CalorieCalculatorTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    PersistenceManager.init(applicationContext)

                    // Restore session from persistent storage
                    SessionManager.token = PersistenceManager.savedToken
                    SessionManager.userId = PersistenceManager.savedUserId
                    SessionManager.userName = PersistenceManager.savedUserName

                    val startDest = if (SessionManager.token != null) "main_graph" else "auth_graph"
                    AppNavigation(startDest)
                }
            }
        }
    }
}

// --- EKRAN TANIMLARI ---
sealed class Screen(val route: String) {
    data object Onboarding1 : Screen("onboarding1")
    data object Onboarding2 : Screen("onboarding2")
    data object Welcome : Screen("welcome")
    data object Login : Screen("login")
    data object Register : Screen("register")
    data object ProfileSetup : Screen("profile_setup")
    data object ActivityLevel : Screen("activity_level")
    data object GoalSetup : Screen("goal_setup")
    data object DietarySetup : Screen("dietary_setup")
    data object Home : Screen("home")
    data object Chatbot : Screen("chatbot")
    data object Calculate : Screen("calculate")
    data object Statistic : Screen("statistic")
    data object Settings : Screen("settings")
}

// --- ANA NAVİGASYON ---
@Composable
fun AppNavigation(startDest: String = "auth_graph") {
    val navController = rememberNavController()
    NavHost(navController = navController, startDestination = startDest) {
        authGraph(navController)
        mainGraph(navController)
    }
}

fun NavGraphBuilder.authGraph(navController: NavController) {
    navigation(startDestination = Screen.Onboarding1.route, route = "auth_graph") {
        composable(Screen.Onboarding1.route) { OnboardingPage(navController, R.drawable.onboarding_bg_food, "Welcome to Calorie Calculator", "Scan your meal with your camera...", Screen.Onboarding2.route) }
        composable(Screen.Onboarding2.route) { OnboardingPage(navController, R.drawable.onboarding_bg_fruits, "About Us", "This application helps you track...", Screen.Welcome.route) }
        composable(Screen.Welcome.route) { WelcomeScreen(navController) }
        composable(Screen.Login.route) { LoginScreen(navController = navController, onLoginSuccess = { navController.navigate("main_graph") { popUpTo("auth_graph") { inclusive = true } } }) }
        composable(Screen.Register.route) { RegisterScreen(navController) }
        composable(Screen.ProfileSetup.route) { ProfileSetupScreen(navController = navController) }
        composable(Screen.ActivityLevel.route) { ActivityLevelScreen(navController = navController) }
        composable(Screen.GoalSetup.route) { GoalSetupScreen(navController = navController) }
        composable(Screen.DietarySetup.route) { DietarySetupScreen(navController = navController, onSetupComplete = { navController.navigate("main_graph") { popUpTo("auth_graph") { inclusive = true } } }) }
    }
}

fun NavGraphBuilder.mainGraph(rootNavController: NavController) {
    composable("main_graph") {
        MainScaffold(onLogout = { 
            rootNavController.navigate("auth_graph") { 
                popUpTo("main_graph") { inclusive = true } 
            } 
        })
    }
}

// --- ANA EKRAN YAPISI ---
@Composable
fun MainScaffold(onLogout: () -> Unit) {
    val context = androidx.compose.ui.platform.LocalContext.current
    PersistenceManager.init(context)
    
    androidx.compose.runtime.LaunchedEffect(Unit) {
        val calendar = java.util.Calendar.getInstance()
        val todayDate = java.text.SimpleDateFormat("yyyy-MM-dd", java.util.Locale.getDefault()).format(calendar.time)
        
        if (PersistenceManager.lastSavedDate != todayDate) {
            if (PersistenceManager.lastSavedDate.isNotEmpty()) {
                val totalYesterday = PersistenceManager.getMealCalorie("breakfast") + PersistenceManager.getMealCalorie("lunch") + PersistenceManager.getMealCalorie("dinner") + PersistenceManager.getMealCalorie("snack")
                val format = java.text.SimpleDateFormat("yyyy-MM-dd", java.util.Locale.getDefault())
                try {
                    val lastDate = format.parse(PersistenceManager.lastSavedDate)
                    if (lastDate != null) {
                        val cal = java.util.Calendar.getInstance()
                        cal.time = lastDate
                        val dayOfWeek = cal.get(java.util.Calendar.DAY_OF_WEEK)
                        val chartIndex = if (dayOfWeek == java.util.Calendar.SUNDAY) 6 else dayOfWeek - 2
                        PersistenceManager.saveHistory(chartIndex, totalYesterday)
                    }
                } catch (e: Exception) {}
            }
            PersistenceManager.resetTodayCalories()
            PersistenceManager.lastSavedDate = todayDate
        }
    }

    val navController = androidx.navigation.compose.rememberNavController()
    Scaffold(
        bottomBar = { AppBottomBar(navController = navController) }
    ) { paddingValues ->
        NavHost(navController = navController, startDestination = Screen.Home.route, Modifier.padding(paddingValues)) {
            composable(Screen.Home.route) { HomeScreen() }
            composable(Screen.Chatbot.route) { ChatbotScreen() }
            composable(Screen.Calculate.route) { CalculateScreen() }
            composable(Screen.Statistic.route) { StatisticScreen() }
            composable(Screen.Settings.route) { SettingsScreen(navController, onLogout) }
        }
    }
}

@Composable
fun AppBottomBar(navController: NavController) {
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route
    NavigationBar(containerColor = Color.White, tonalElevation = 12.dp) {
        val colors = NavigationBarItemDefaults.colors(indicatorColor = LightGreenBg, selectedIconColor = PrimaryGreen, selectedTextColor = PrimaryGreen, unselectedIconColor = TextGray, unselectedTextColor = TextGray)
        NavigationBarItem(icon = { Icon(Icons.Filled.Home, stringResource(R.string.nav_home)) }, label = { Text(stringResource(R.string.nav_home), fontWeight = FontWeight.Medium) }, selected = currentRoute == Screen.Home.route, onClick = { navController.navigate(Screen.Home.route) }, colors = colors)
        NavigationBarItem(icon = { Icon(Icons.AutoMirrored.Filled.Chat, stringResource(R.string.nav_chatbot)) }, label = { Text(stringResource(R.string.nav_chatbot), fontWeight = FontWeight.Medium) }, selected = currentRoute == Screen.Chatbot.route, onClick = { navController.navigate(Screen.Chatbot.route) }, colors = colors)
        NavigationBarItem(icon = { Icon(Icons.Filled.CameraAlt, stringResource(R.string.nav_calculate)) }, label = { Text(stringResource(R.string.nav_calculate), fontWeight = FontWeight.Medium) }, selected = currentRoute == Screen.Calculate.route, onClick = { navController.navigate(Screen.Calculate.route) }, colors = colors)
        NavigationBarItem(icon = { Icon(Icons.Filled.RestaurantMenu, stringResource(R.string.nav_statistic)) }, label = { Text(stringResource(R.string.nav_statistic), fontWeight = FontWeight.Medium) }, selected = currentRoute == Screen.Statistic.route, onClick = { navController.navigate(Screen.Statistic.route) }, colors = colors)
        NavigationBarItem(icon = { Icon(Icons.Filled.Settings, stringResource(R.string.nav_settings)) }, label = { Text(stringResource(R.string.nav_settings), fontWeight = FontWeight.Medium) }, selected = currentRoute == Screen.Settings.route, onClick = { navController.navigate(Screen.Settings.route) }, colors = colors)
    }
}

// --- 1. SETTINGS SCREEN ---
@Composable
fun SettingsScreen(navController: NavController, onLogout: () -> Unit) {
    val coroutineScope = rememberCoroutineScope()
    val context = LocalContext.current

    var showNameDialog by remember { mutableStateOf(false) }
    var showPersonalDialog by remember { mutableStateOf(false) }
    var showEmailDialog by remember { mutableStateOf(false) }
    var showLanguageDialog by remember { mutableStateOf(false) }

    var nameInput by remember { mutableStateOf("") }
    var ageInput by remember { mutableStateOf("") }
    var genderInput by remember { mutableStateOf("") }
    var heightInput by remember { mutableStateOf("") }
    var weightInput by remember { mutableStateOf("") }
    var emailInput by remember { mutableStateOf("") }

    LazyColumn(modifier = Modifier.fillMaxSize().background(SoftWhite).padding(16.dp), contentPadding = PaddingValues(bottom = 80.dp)) {
        item { Text(stringResource(R.string.settings_title), fontSize = 28.sp, fontWeight = FontWeight.Bold); Spacer(modifier = Modifier.height(24.dp)) }
        item { SettingsSection(title = stringResource(R.string.account_section)) }
        item { SettingsItem(title = stringResource(R.string.edit_profile), icon = Icons.Filled.Person, onClick = { showNameDialog = true }) }
        item { SettingsItem(title = stringResource(R.string.change_email), icon = Icons.Filled.Email, onClick = { showEmailDialog = true }) }
        item { Spacer(modifier = Modifier.height(24.dp)) }
        item { SettingsSection(title = stringResource(R.string.personalization_section)) }
        item { SettingsItem(title = stringResource(R.string.height_weight), icon = Icons.Filled.Scale, onClick = { showPersonalDialog = true }) }
        item { Spacer(modifier = Modifier.height(24.dp)) }
        item { SettingsSection(title = stringResource(R.string.general_section)) }
        item { SettingsItem(title = stringResource(R.string.language), subtitle = stringResource(R.string.current_language), icon = Icons.Filled.Language, onClick = { showLanguageDialog = true }) }
        item { Spacer(modifier = Modifier.height(40.dp)) }
        item {
            OutlinedButton(
                onClick = { 
                    SessionManager.token = null
                    PersistenceManager.savedToken = null
                    onLogout()
                },
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                border = BorderStroke(1.dp, Color.Red.copy(alpha = 0.5f))
            ) {
                Text(stringResource(R.string.logout), color = Color.Red, fontWeight = FontWeight.Bold)
            }
            Spacer(modifier = Modifier.height(16.dp))
            OutlinedButton(
                onClick = { 
                    (context as? android.app.Activity)?.finishAndRemoveTask()
                    kotlin.system.exitProcess(0)
                },
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                border = BorderStroke(1.dp, Color.DarkGray)
            ) {
                Text("Uygulamayı Kapat", color = Color.DarkGray, fontWeight = FontWeight.Bold)
            }
        }
    }

    if (showNameDialog) {
        AlertDialog(onDismissRequest = { showNameDialog = false }, title = { Text(stringResource(R.string.edit_profile)) },
            text = { 
                Column {
                    OutlinedTextField(value = nameInput, onValueChange = { nameInput = it }, label = { Text(stringResource(R.string.full_name_label)) }, modifier = Modifier.fillMaxWidth())
                    Spacer(modifier = Modifier.height(8.dp))
                    OutlinedTextField(value = ageInput, onValueChange = { ageInput = it }, label = { Text(stringResource(R.string.age_label)) }, modifier = Modifier.fillMaxWidth())
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(stringResource(R.string.gender_label), fontWeight = FontWeight.SemiBold, modifier = Modifier.padding(start = 4.dp))
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        RadioButton(selected = genderInput == "Erkek", onClick = { genderInput = "Erkek" })
                        Text(stringResource(R.string.male), modifier = Modifier.clickable { genderInput = "Erkek" })
                        Spacer(modifier = Modifier.width(8.dp))
                        RadioButton(selected = genderInput == "Kadın", onClick = { genderInput = "Kadın" })
                        Text(stringResource(R.string.female), modifier = Modifier.clickable { genderInput = "Kadın" })
                    }
                }
            },
            confirmButton = { TextButton(onClick = {
                val token = SessionManager.token
                if (!token.isNullOrEmpty()) {
                    coroutineScope.launch { 
                        try { 
                            RetrofitClient.instance.updateUserInfo(token, UserUpdate(
                                full_name = nameInput,
                                yas = ageInput.toIntOrNull(),
                                cinsiyet = genderInput
                            ))
                            if (nameInput.isNotBlank()) {
                                SessionManager.userName = nameInput
                            }
                            showNameDialog = false 
                        } catch(e:Exception){ 
                            Toast.makeText(context, "${context.getString(R.string.error_message)}: ${e.localizedMessage}", Toast.LENGTH_SHORT).show() 
                        } 
                    }
                } else {
                    Toast.makeText(context, "Lütfen önce giriş yapın.", Toast.LENGTH_SHORT).show()
                }
            }) { Text(stringResource(R.string.save_button)) } }
        )
    }

    if (showPersonalDialog) {
        AlertDialog(onDismissRequest = { showPersonalDialog = false }, title = { Text(stringResource(R.string.height_weight)) },
            text = { Column {
                OutlinedTextField(value = heightInput, onValueChange = { heightInput = it }, label = { Text(stringResource(R.string.height_label)) })
                Spacer(Modifier.height(8.dp))
                OutlinedTextField(value = weightInput, onValueChange = { weightInput = it }, label = { Text(stringResource(R.string.weight_label)) })
            } },
            confirmButton = { TextButton(onClick = {
                val token = SessionManager.token
                if (!token.isNullOrEmpty()) {
                    coroutineScope.launch { 
                        try { 
                            RetrofitClient.instance.updateUserInfo(token, UserUpdate(boy_cm = heightInput.toFloatOrNull(), kilo_kg = weightInput.toFloatOrNull()))
                            showPersonalDialog = false 
                        } catch(e:Exception){ 
                            Toast.makeText(context, "${context.getString(R.string.error_message)}: ${e.localizedMessage}", Toast.LENGTH_SHORT).show()
                        } 
                    }
                } else {
                    Toast.makeText(context, "Lütfen önce giriş yapın.", Toast.LENGTH_SHORT).show()
                }
            }) { Text(stringResource(R.string.save_button)) } }
        )
    }

    if (showEmailDialog) {
        AlertDialog(onDismissRequest = { showEmailDialog = false }, title = { Text(stringResource(R.string.change_email)) },
            text = { OutlinedTextField(value = emailInput, onValueChange = { emailInput = it }, label = { Text(stringResource(R.string.new_email_label)) }) },
            confirmButton = { TextButton(onClick = {
                val token = SessionManager.token
                if (!token.isNullOrEmpty()) {
                    coroutineScope.launch { 
                        try { 
                            RetrofitClient.instance.updateUserInfo(token, UserUpdate(email = emailInput))
                            showEmailDialog = false 
                        } catch(e:Exception){ 
                            Toast.makeText(context, "${context.getString(R.string.error_message)}: ${e.localizedMessage}", Toast.LENGTH_SHORT).show() 
                        } 
                    }
                } else {
                    Toast.makeText(context, "Lütfen önce giriş yapın.", Toast.LENGTH_SHORT).show()
                }
            }) { Text(stringResource(R.string.save_button)) } }
        )
    }

    if (showLanguageDialog) {
        AlertDialog(
            onDismissRequest = { showLanguageDialog = false },
            title = { Text(stringResource(R.string.select_language)) },
            text = {
                Column {
                    TextButton(onClick = {
                        val localeList = androidx.core.os.LocaleListCompat.forLanguageTags("en")
                        AppCompatDelegate.setApplicationLocales(localeList)
                        val token = SessionManager.token
                        if (!token.isNullOrEmpty()) {
                            coroutineScope.launch { try { RetrofitClient.instance.updateUserInfo(token, UserUpdate(language = "English")) } catch(e:Exception){} }
                        }
                        showLanguageDialog = false
                    }, modifier = Modifier.fillMaxWidth()) { Text(stringResource(R.string.english)) }
                    TextButton(onClick = {
                        val localeList = androidx.core.os.LocaleListCompat.forLanguageTags("tr")
                        AppCompatDelegate.setApplicationLocales(localeList)
                        val token = SessionManager.token
                        if (!token.isNullOrEmpty()) {
                            coroutineScope.launch { try { RetrofitClient.instance.updateUserInfo(token, UserUpdate(language = "Turkish")) } catch(e:Exception){} }
                        }
                        showLanguageDialog = false
                    }, modifier = Modifier.fillMaxWidth()) { Text(stringResource(R.string.turkish)) }
                }
            },
            confirmButton = { }
        )
    }
}

// --- 2. CALCULATE SCREEN ---
@Composable
fun CalculateScreen() {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    var selectedImageUri by remember { mutableStateOf<Uri?>(null) }
    var capturedImageBitmap by remember { mutableStateOf<Bitmap?>(null) }
    var isCalculating by remember { mutableStateOf(false) }
    var apiResult by remember { mutableStateOf<FoodAnalysisResponse?>(null) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    
    // Yardımcı fonksiyon: String içinden kalori sayısını çekme
    fun extractCalories(input: String?): Float {
        if (input == null) return 0f
        val digits = input.filter { it.isDigit() }.ifEmpty { "0" }
        return digits.toFloatOrNull() ?: 0f
    }
    
    var breakfastCals by remember { mutableFloatStateOf(PersistenceManager.getMealCalorie("breakfast")) }
    var lunchCals by remember { mutableFloatStateOf(PersistenceManager.getMealCalorie("lunch")) }
    var dinnerCals by remember { mutableFloatStateOf(PersistenceManager.getMealCalorie("dinner")) }
    var snackCals by remember { mutableFloatStateOf(PersistenceManager.getMealCalorie("snack")) }
    
    var selectedMeal by remember { mutableStateOf<String?>(null) }
    var manualAddMeal by remember { mutableStateOf<String?>(null) }
    var manualCalorieInput by remember { mutableStateOf("") }
    val mealOptions = listOf(stringResource(R.string.meal_breakfast), stringResource(R.string.meal_lunch), stringResource(R.string.meal_dinner), stringResource(R.string.meal_snack))

    val galleryLauncher = rememberLauncherForActivityResult(ActivityResultContracts.PickVisualMedia()) { uri ->
        if (uri != null) { selectedImageUri = uri; capturedImageBitmap = null; apiResult = null; selectedMeal = null }
    }
    val cameraLauncher = rememberLauncherForActivityResult(ActivityResultContracts.TakePicturePreview()) { bitmap ->
        if (bitmap != null) { capturedImageBitmap = bitmap; selectedImageUri = null; apiResult = null; selectedMeal = null }
    }

    Column(modifier = Modifier.fillMaxSize().background(SoftWhite).padding(horizontal = 24.dp).verticalScroll(rememberScrollState()), horizontalAlignment = Alignment.CenterHorizontally) {
        Spacer(modifier = Modifier.height(24.dp))
        Text(stringResource(R.string.calculate_title), fontSize = 28.sp, fontWeight = FontWeight.Bold)
        Spacer(modifier = Modifier.height(24.dp))
        Card(modifier = Modifier.fillMaxWidth().height(260.dp), shape = RoundedCornerShape(24.dp), colors = CardDefaults.cardColors(containerColor = Color.White)) {
            Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                if (capturedImageBitmap != null) Image(bitmap = capturedImageBitmap!!.asImageBitmap(), contentDescription = null, contentScale = ContentScale.Crop, modifier = Modifier.fillMaxSize())
                else if (selectedImageUri != null) {
                    androidx.compose.ui.viewinterop.AndroidView(factory = { ctx -> android.widget.ImageView(ctx).apply { scaleType = android.widget.ImageView.ScaleType.CENTER_CROP; setImageURI(selectedImageUri) } }, modifier = Modifier.fillMaxSize())
                }
                else Icon(Icons.Filled.CameraAlt, null, modifier = Modifier.size(60.dp), tint = Color.LightGray)
            }
        }
        Spacer(modifier = Modifier.height(20.dp))
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceEvenly) {
            Button(onClick = { cameraLauncher.launch(null) }, colors = ButtonDefaults.buttonColors(containerColor = PrimaryGreen)) { Text(stringResource(R.string.camera_button)) }
            Button(onClick = { galleryLauncher.launch(PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly)) }, colors = ButtonDefaults.buttonColors(containerColor = PrimaryGreen)) { Text(stringResource(R.string.gallery_button)) }
        }
        
        Button(
            onClick = {
                isCalculating = true
                errorMessage = null
                coroutineScope.launch {
                    try {
                        val imagePart = if (capturedImageBitmap != null) ImageUtils.bitmapToMultipart(capturedImageBitmap!!, context)
                        else if (selectedImageUri != null) ImageUtils.uriToMultipart(selectedImageUri!!, context) else null
                        
                        if (imagePart != null) {
                            apiResult = RetrofitClient.instance.analyzeFood(imagePart)
                        } else {
                            errorMessage = "Lütfen bir fotoğraf seçin."
                        }
                    } catch (e: Exception) { errorMessage = e.localizedMessage }
                    finally { isCalculating = false }
                }
            },
            modifier = Modifier.fillMaxWidth().height(56.dp).padding(vertical = 12.dp),
            enabled = (selectedImageUri != null || capturedImageBitmap != null) && !isCalculating,
            colors = ButtonDefaults.buttonColors(containerColor = PrimaryGreen)
        ) {
            if (isCalculating) CircularProgressIndicator(color = Color.White, modifier = Modifier.size(24.dp))
            else Text(stringResource(R.string.calculate_action_button), fontWeight = FontWeight.Bold)
        }

        if (apiResult != null) {
            Card(modifier = Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(containerColor = LeafGreen.copy(alpha = 0.2f))) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Tahmin: " + (apiResult?.food_name ?: ""), fontWeight = FontWeight.Bold)
                    Text("Porsiyon: " + (apiResult?.portion ?: ""), fontSize = 14.sp)
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(stringResource(R.string.calories_label) + "${apiResult?.calories} kcal", color = PrimaryGreen, fontWeight = FontWeight.Bold)
                    Text("Protein: ${apiResult?.macros?.protein}g | Karbonhidrat: ${apiResult?.macros?.carbs}g | Yağ: ${apiResult?.macros?.fat}g", fontSize = 12.sp, color = TextGray)
                }
            }
            Spacer(modifier = Modifier.height(16.dp))
            Text(stringResource(R.string.ask_which_meal), fontWeight = FontWeight.SemiBold, color = TextGray)
            Spacer(modifier = Modifier.height(8.dp))
            Row(modifier = Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                mealOptions.forEach { meal ->
                    val isSelected = selectedMeal == meal
                    Surface(
                        modifier = Modifier.clickable { selectedMeal = meal },
                        shape = RoundedCornerShape(16.dp),
                        color = if (isSelected) PrimaryGreen else Color.White,
                        border = BorderStroke(1.dp, PrimaryGreen)
                    ) {
                        Text(meal, color = if (isSelected) Color.White else PrimaryGreen, modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp))
                    }
                }
            }

            if (selectedMeal != null) {
                Spacer(modifier = Modifier.height(12.dp))
                Button(onClick = {
                    val currentApiResult = apiResult
                    val currentMeal = selectedMeal
                    val mealOpt0 = mealOptions[0]
                    val mealOpt1 = mealOptions[1]
                    val mealOpt2 = mealOptions[2]
                    val mealOpt3 = mealOptions[3]
                    
                    if (currentApiResult != null && currentMeal != null) {
                        val caloriesValue = currentApiResult.calories.toFloat()
                        val foodName = currentApiResult.food_name

                        coroutineScope.launch {
                            try {
                                val token = SessionManager.token ?: ""
                                if (token.isNotEmpty()) {
                                    val mealData = MealCreate(
                                        food_name = "${currentMeal}: ${foodName}", 
                                        calories = caloriesValue,
                                        protein = 0f, 
                                        fat = 0f,
                                        carbs = 0f
                                    )
                                    RetrofitClient.instance.saveMeal(token, mealData)
                                }
                            } catch (e: Exception) { }
                        }

                        when (currentMeal) {
                            mealOpt0 -> { breakfastCals += caloriesValue; PersistenceManager.saveMealCalorie("breakfast", breakfastCals) }
                            mealOpt1 -> { lunchCals += caloriesValue; PersistenceManager.saveMealCalorie("lunch", lunchCals) }
                            mealOpt2 -> { dinnerCals += caloriesValue; PersistenceManager.saveMealCalorie("dinner", dinnerCals) }
                            mealOpt3 -> { snackCals += caloriesValue; PersistenceManager.saveMealCalorie("snack", snackCals) }
                        }
                    }

                    apiResult = null
                    selectedImageUri = null
                    capturedImageBitmap = null
                    selectedMeal = null
                }, modifier = Modifier.fillMaxWidth(), colors = ButtonDefaults.buttonColors(containerColor = PrimaryGreen)) {
                    Text(stringResource(R.string.add_button_meal), fontWeight = FontWeight.Bold)
            }
        }
    }
        
    if (errorMessage != null) Text(errorMessage!!, color = Color.Red, modifier = Modifier.padding(top = 10.dp))
        
    Spacer(modifier = Modifier.height(32.dp))
    Text(stringResource(R.string.todays_meals), fontSize = 20.sp, fontWeight = FontWeight.Bold, color = Color(0xFF222222), modifier = Modifier.align(Alignment.Start))
    Spacer(modifier = Modifier.height(16.dp))
        
        InteractiveMealCard(stringResource(R.string.meal_breakfast), "${breakfastCals.toInt()} " + stringResource(R.string.kcal_unit)) { manualAddMeal = "breakfast" }
        InteractiveMealCard(stringResource(R.string.meal_lunch), "${lunchCals.toInt()} " + stringResource(R.string.kcal_unit)) { manualAddMeal = "lunch" }
        InteractiveMealCard(stringResource(R.string.meal_dinner), "${dinnerCals.toInt()} " + stringResource(R.string.kcal_unit)) { manualAddMeal = "dinner" }
        InteractiveMealCard(stringResource(R.string.meal_snack), "${snackCals.toInt()} " + stringResource(R.string.kcal_unit)) { manualAddMeal = "snack" }
        
        Spacer(modifier = Modifier.height(80.dp))
        
        if (manualAddMeal != null) {
            val manualSuffix = stringResource(R.string.manual_suffix)
            androidx.compose.material3.AlertDialog(
                onDismissRequest = { manualAddMeal = null },
                title = { Text(stringResource(R.string.manual_add_title)) },
                text = {
                    androidx.compose.material3.OutlinedTextField(
                        value = manualCalorieInput,
                        onValueChange = { manualCalorieInput = it },
                        keyboardOptions = androidx.compose.foundation.text.KeyboardOptions(keyboardType = androidx.compose.ui.text.input.KeyboardType.Number),
                        label = { Text(stringResource(R.string.manual_add_label)) }
                    )
                },
                confirmButton = {
                    Button(onClick = {
                        val addedCals = manualCalorieInput.toFloatOrNull() ?: 0f
                        if (addedCals > 0) {
                            val mealNameString = when (manualAddMeal) { "breakfast" -> mealOptions[0]; "lunch" -> mealOptions[1]; "dinner" -> mealOptions[2]; else -> mealOptions[3] }
                            when (manualAddMeal) {
                                "breakfast" -> { breakfastCals += addedCals; PersistenceManager.saveMealCalorie("breakfast", breakfastCals) }
                                "lunch" -> { lunchCals += addedCals; PersistenceManager.saveMealCalorie("lunch", lunchCals) }
                                "dinner" -> { dinnerCals += addedCals; PersistenceManager.saveMealCalorie("dinner", dinnerCals) }
                                "snack" -> { snackCals += addedCals; PersistenceManager.saveMealCalorie("snack", snackCals) }
                            }
                            coroutineScope.launch {
                                try {
                                    val token = SessionManager.token ?: ""
                                    if (token.isNotEmpty()) { RetrofitClient.instance.saveMeal(token, MealCreate("$mealNameString $manualSuffix", addedCals, 0f, 0f, 0f)) }
                                } catch(e: Exception) {}
                            }
                        }
                        manualAddMeal = null
                        manualCalorieInput = ""
                    }) {
                        Text(stringResource(R.string.add_button_meal))
                    }
                },
                dismissButton = {
                    androidx.compose.material3.TextButton(onClick = { manualAddMeal = null; manualCalorieInput = "" }) { Text(stringResource(R.string.cancel)) }
                }
            )
        }
    }
}

// --- STATIK TARIF VERI SETI ---
val staticHealthyRecipes = listOf(
    Recipe(
        name = "Avokadolu Tam Buğday Tost",
        description = "Sağlıklı yağlar ve kompleks karbonhidratlarla dolu, güne enerjik başlamanı sağlayacak harika bir kahvaltı seçeneği.",
        ingredients = listOf("2 dilim tam buğday ekmeği", "1 adet olgun avokado", "1 yemek kaşığı zeytinyağı", "Limon suyu, tuz, karabiber", "İsteğe bağlı: Çeri domates, çörek otu"),
        steps = listOf(
            "Ekmekleri hafifçe kızartın.",
            "Avokadoyu bir kasede ezin, içine zeytinyağı, birkaç damla limon suyu, tuz ve karabiber ekleyin.",
            "Ezilmiş avokadoyu kızarmış ekmeklerin üzerine kalın bir tabaka halinde sürün.",
            "Üzerine dilimlenmiş çeri domates ve çörek otu serpiştirerek servis yapın."
        ),
        calories = "288 kcal | Protein: 6g | Karb: 28g | Yağ: 18g",
        imageRes = R.drawable.avovado
    ),
    Recipe(
        name = "Izgara Somon ve Kinoa",
        description = "Yüksek Omega-3 ve protein içeren, akşam yemekleri için hafif ama çok doyurucu bir tarif.",
        ingredients = listOf("150g somon fileto", "3 yemek kaşığı haşlanmış kinoa", "Yarım demet kuşkonmaz", "1 tatlı kaşığı zeytinyağı", "Limon, tuz, karabiber"),
        steps = listOf(
            "Somonu zeytinyağı, tuz ve karabiber ile marine edin.",
            "Kuşkonmazları fırın tepsisine dizip hafifçe yağlayın.",
            "Somonu ve kuşkonmazları önceden ısıtılmış 200 derece fırında veya ızgarada 12-15 dakika pişirin.",
            "Haşlanmış kinoa yatağında limon dilimleriyle servis yapın."
        ),
        calories = "350 kcal | Protein: 32g | Karb: 15g | Yağ: 18g",
        imageRes = R.drawable.grilled_salmon
    ),
    Recipe(
        name = "Fit Orman Meyveli Yulaf",
        description = "Tatlı krizlerini kesen, lif oranı yüksek ve bağırsak dostu fit yulaf lapası.",
        ingredients = listOf("4 yemek kaşığı yulaf ezmesi", "1 su bardağı badem sütü (veya yarım yağlı süt)", "Yarım muz", "1 avuç yaban mersini veya böğürtlen", "1 tatlı kaşığı chia tohumu"),
        steps = listOf(
            "Yulaf ve sütü küçük bir tencereye alın, kısık ateşte lapa kıvamına gelene kadar pişirin.",
            "İçine chia tohumunu ekleyip karıştırın ve ocaktan alın.",
            "Kaseye aldığınız yulafın üzerini muz dilimleri ve orman meyveleriyle süsleyin.",
            "İsteğe bağlı olarak 1 çay kaşığı tarçın veya bal gezdirebilirsiniz."
        ),
        calories = "220 kcal | Protein: 8g | Karb: 36g | Yağ: 5g",
        imageRes = R.drawable.forest_fruit_oats
    ),
    Recipe(
        name = "Fırınlanmış Çıtır Nohut Salata",
        description = "Bitkisel protein deposu, doyurucu ve çok pratik bir vegan salata.",
        ingredients = listOf("1 su bardağı haşlanmış nohut", "1 tatlı kaşığı zeytinyağı, toz biber, kimyon", "Yarım demet marul", "Çeri domates, salatalık", "1 yemek kaşığı limon suyu"),
        steps = listOf(
            "Nohutları zeytinyağı ve baharatlarla harmanlayıp 200 derece fırında 15 dakika çıtırlaşana kadar pişirin.",
            "Yeşillikleri doğrayıp geniş bir kaseye alın.",
            "Üzerine çıtır nohutları ekleyin.",
            "Limon suyu ve çok az zeytinyağı gezdirerek servis yapın."
        ),
        calories = "210 kcal | Protein: 12g | Karb: 28g | Yağ: 6g",
        imageRes = R.drawable.baked_chickpeas
    ),
    Recipe(
        name = "Fıstık Ezmeli Muzlu Smoothie",
        description = "Antrenman öncesi veya sonrası için ideal, hızlı enerji veren sıvı öğün.",
        ingredients = listOf("1 adet donmuş muz", "1 yemek kaşığı şekersiz fıstık ezmesi", "1 su bardağı süt", "1 çay kaşığı tarçın"),
        steps = listOf(
            "Tüm malzemeleri blendera ekleyin.",
            "Pürüzsüz ve kremsi bir kıvam alana kadar yüksek devirde çekin.",
            "Soğuk servis yapın."
        ),
        calories = "310 kcal | Protein: 14g | Karb: 38g | Yağ: 12g"
    ),
    Recipe(
        name = "Sebzeli Mantarlı Omlet",
        description = "Düşük karbonhidratlı, yüksek proteinli ve çok lezzetli kahvaltı alternatifi.",
        ingredients = listOf("2 adet yumurta", "3-4 adet kültür mantarı", "1 avuç ıspanak", "1 çay kaşığı tereyağı", "Tuz, karabiber, pulbiber"),
        steps = listOf(
            "Mantarları ince ince dilimleyin ve tereyağında hafifçe soteleyin.",
            "Üzerine ıspanakları ekleyip sönene kadar 1-2 dakika daha soteleyin.",
            "Yumurtaları bir kasede çırpın, tuz ve baharatları ekleyin.",
            "Çırpılmış yumurtayı tavaya dökün ve kısık ateşte pişirin."
        ),
        calories = "190 kcal | Protein: 14g | Karb: 4g | Yağ: 14g"
    )
)

data class IngredientItem(val name: String, val amount: String)

// --- 3. NE YESEM (RECIPE) SCREEN ---
@OptIn(ExperimentalLayoutApi::class)
@Composable
fun StatisticScreen() {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    
    var selectedImageUri by remember { mutableStateOf<Uri?>(null) }
    var capturedImageBitmap by remember { mutableStateOf<Bitmap?>(null) }
    var isLoading by remember { mutableStateOf(false) }
    var recipeResult by remember { mutableStateOf<RecipeResponse?>(null) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    var isFabExpanded by remember { mutableStateOf(false) }
    
    var isManualInputScreenOpen by remember { mutableStateOf(false) }
    var ingredientList by remember { mutableStateOf(listOf<IngredientItem>()) }
    var currentIngredient by remember { mutableStateOf("") }
    var currentAmount by remember { mutableStateOf("") }
    
    var selectedTab by remember { mutableStateOf("Tüm Tarifler") }
    var favoriteRecipeNames by remember { mutableStateOf(PersistenceManager.favoriteRecipes) }
    var searchQuery by remember { mutableStateOf("") }

    val loadingPhrases = listOf("Malzemeler hazırlanıyor...", "Yapay zeka şefi tabağını inceliyor...", "Kaloriler hesaplanıyor...", "Özel tarifler yazılıyor...")
    var currentPhraseIndex by remember { mutableIntStateOf(0) }

    LaunchedEffect(isLoading) {
        if (isLoading) {
            currentPhraseIndex = 0
            while(true) {
                kotlinx.coroutines.delay(2000)
                currentPhraseIndex = (currentPhraseIndex + 1) % loadingPhrases.size
            }
        }
    }

    val fetchAiRecipe: (Bitmap?, Uri?, String?) -> Unit = { bmp, uri, text ->
        isLoading = true
        errorMessage = null
        recipeResult = null
        coroutineScope.launch {
            try {
                val imagePart = if (bmp != null) ImageUtils.bitmapToMultipart(bmp, context)
                else if (uri != null) ImageUtils.uriToMultipart(uri, context) else null
                
                val textPart = if (!text.isNullOrBlank()) text.toRequestBody("text/plain".toMediaTypeOrNull()) else null

                if (imagePart != null || textPart != null) {
                    val maxCal = PersistenceManager.getTargetCalories()
                    val eatenCal = PersistenceManager.getMealCalorie("breakfast") + PersistenceManager.getMealCalorie("lunch") + PersistenceManager.getMealCalorie("dinner") + PersistenceManager.getMealCalorie("snack")
                    val leftCal = (maxCal - eatenCal).toInt().coerceAtLeast(0).toString()
                    val restr = PersistenceManager.dietaryRestrictions.ifBlank { null }
                    
                    recipeResult = RetrofitClient.instance.getRecipeRecommendations(imagePart, textPart, leftCal, restr)
                } else {
                    errorMessage = "Lütfen önce bir fotoğraf çekin, seçin veya malzeme girin."
                }
            } catch (e: Exception) { errorMessage = e.localizedMessage }
            finally { isLoading = false }
        }
    }

    val galleryLauncher = rememberLauncherForActivityResult(ActivityResultContracts.PickVisualMedia()) { uri ->
        if (uri != null) { selectedImageUri = uri; capturedImageBitmap = null; fetchAiRecipe(null, uri, null) }
    }
    val cameraLauncher = rememberLauncherForActivityResult(ActivityResultContracts.TakePicturePreview()) { bitmap ->
        if (bitmap != null) { capturedImageBitmap = bitmap; selectedImageUri = null; fetchAiRecipe(bitmap, null, null) }
    }

    // Removed old AlertDialog

    Box(modifier = Modifier.fillMaxSize().background(SoftWhite)) {
        LazyColumn(modifier = Modifier.fillMaxSize().padding(horizontal = 16.dp), contentPadding = PaddingValues(top = 24.dp, bottom = 100.dp), horizontalAlignment = Alignment.CenterHorizontally) {
            // Ne Yesem? başlığı kaldırıldı. Arama çubuğu en üstte görünecek.

            if (isLoading) {
                item {
                    Column(modifier = Modifier.fillMaxWidth().padding(32.dp).height(300.dp), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
                        CircularProgressIndicator(color = PrimaryGreen, modifier = Modifier.size(72.dp), strokeWidth = 6.dp)
                        Spacer(modifier = Modifier.height(24.dp))
                        Text(loadingPhrases[currentPhraseIndex], color = PrimaryGreen, fontWeight = FontWeight.Bold, fontSize = 18.sp, textAlign = androidx.compose.ui.text.style.TextAlign.Center)
                    }
                }
            }

            if (errorMessage != null) {
                item {
                    Text(errorMessage!!, color = Color.Red, modifier = Modifier.padding(top = 8.dp))
                    Spacer(modifier = Modifier.height(24.dp))
                }
            }

            if (recipeResult != null) {
                item {
                    Row(modifier = Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                        IconButton(onClick = { recipeResult = null; selectedImageUri = null; capturedImageBitmap = null }) {
                            Icon(Icons.Filled.ArrowBack, contentDescription = "Geri Dön", tint = PrimaryGreen)
                        }
                        Text("✨ Şefin Önerileri", fontWeight = FontWeight.Bold, fontSize = 20.sp, color = PrimaryGreen, modifier = Modifier.weight(1f))
                    }
                    Divider(modifier = Modifier.padding(bottom = 8.dp))
                    
                    if (recipeResult?.status == "success") {
                        if (!recipeResult?.detected_ingredients.isNullOrEmpty()) {
                            Text(stringResource(R.string.detected_ingredients_title), fontWeight = FontWeight.SemiBold, modifier = Modifier.fillMaxWidth())
                            FlowRow(modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp), horizontalArrangement = Arrangement.spacedBy(8.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                                recipeResult?.detected_ingredients?.forEach { ingredient ->
                                    Surface(shape = RoundedCornerShape(20.dp), color = LeafGreen.copy(alpha = 0.15f), border = BorderStroke(1.dp, LeafGreen.copy(alpha = 0.3f))) {
                                        Text(text = ingredient, modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp), fontSize = 12.sp, color = Color(0xFF2E7D32))
                                    }
                                }
                            }
                            Spacer(modifier = Modifier.height(16.dp))
                        }
                    } else {
                        Text("Sunucu Hatası: ${recipeResult?.status}", color = Color.Red, modifier = Modifier.fillMaxWidth())
                    }
                }

                if (recipeResult?.status == "success") {
                    val recipes = recipeResult?.recommendations?.recipes ?: emptyList()
                    if (recipes.isEmpty() && !(recipeResult?.detected_ingredients.isNullOrEmpty())) {
                        item { Text("Malzemelere uygun tarif bulunamadı.", color = TextGray) }
                    } else {
                        items(recipes) { recipe ->
                            RecipeCard(
                                recipe = recipe,
                                isFavorite = favoriteRecipeNames.contains(recipe.name),
                                onFavoriteToggle = {
                                    val newFavs = favoriteRecipeNames.toMutableSet()
                                    if (newFavs.contains(recipe.name)) newFavs.remove(recipe.name) else newFavs.add(recipe.name)
                                    PersistenceManager.favoriteRecipes = newFavs
                                    favoriteRecipeNames = newFavs
                                },
                                onAddClick = {
                                    val currentCals = PersistenceManager.getMealCalorie("snack")
                                    val calValue = recipe.calories.split(" ").firstOrNull()?.toFloatOrNull() ?: 0f
                                    PersistenceManager.saveMealCalorie("snack", currentCals + calValue)
                                    android.widget.Toast.makeText(context, "${recipe.name} Atıştırmalık öğününe eklendi!", android.widget.Toast.LENGTH_SHORT).show()
                                }
                            )
                            Spacer(modifier = Modifier.height(16.dp))
                        }
                    }
                }
            } else if (!isLoading) {
                // Eğer AI sonucu yoksa varsayılan hazır tarifleri göster
                item {
                    Column(modifier = Modifier.fillMaxWidth().padding(bottom = 16.dp)) {
                        // Search Bar
                        OutlinedTextField(
                            value = searchQuery,
                            onValueChange = { searchQuery = it },
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(bottom = 16.dp),
                            placeholder = { Text("Tarif ara...") },
                            leadingIcon = { Icon(Icons.Filled.Search, contentDescription = "Ara", tint = PrimaryGreen) },
                            trailingIcon = {
                                if (searchQuery.isNotEmpty()) {
                                    IconButton(onClick = { searchQuery = "" }) {
                                        Icon(Icons.Filled.Clear, contentDescription = "Temizle", tint = TextGray)
                                    }
                                }
                            },
                            shape = RoundedCornerShape(16.dp),
                            singleLine = true,
                            colors = androidx.compose.material3.OutlinedTextFieldDefaults.colors(
                                focusedBorderColor = PrimaryGreen,
                                unfocusedBorderColor = Color.LightGray,
                                focusedContainerColor = SoftWhite,
                                unfocusedContainerColor = SoftWhite
                            )
                        )
                        
                        // Tabs
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                            val tabs = listOf("Tüm Tarifler", "Favorilerim")
                            tabs.forEach { tab ->
                                val isSelected = selectedTab == tab
                                Surface(
                                    modifier = Modifier.weight(1f).clickable { selectedTab = tab },
                                    shape = RoundedCornerShape(20.dp),
                                    color = if (isSelected) PrimaryGreen else SoftWhite,
                                    border = if (!isSelected) BorderStroke(1.dp, Color.LightGray) else null
                                ) {
                                    Text(
                                        text = tab,
                                        modifier = Modifier.padding(vertical = 10.dp),
                                        textAlign = androidx.compose.ui.text.style.TextAlign.Center,
                                        color = if (isSelected) Color.White else TextGray,
                                        fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium
                                    )
                                }
                            }
                        }
                    }
                }
                
                val recipesToShow = staticHealthyRecipes.filter { recipe ->
                    val matchesTab = if (selectedTab == "Favorilerim") favoriteRecipeNames.contains(recipe.name) else true
                    val matchesSearch = recipe.name.contains(searchQuery, ignoreCase = true)
                    matchesTab && matchesSearch
                }

                if (recipesToShow.isEmpty() && selectedTab == "Favorilerim") {
                    item { Text("Henüz favori tarifiniz yok.", color = Color.Gray, modifier = Modifier.padding(top = 16.dp)) }
                } else {
                    items(recipesToShow) { recipe ->
                        RecipeCard(
                            recipe = recipe,
                            isFavorite = favoriteRecipeNames.contains(recipe.name),
                            onFavoriteToggle = {
                                val newFavs = favoriteRecipeNames.toMutableSet()
                                if (newFavs.contains(recipe.name)) newFavs.remove(recipe.name) else newFavs.add(recipe.name)
                                PersistenceManager.favoriteRecipes = newFavs
                                favoriteRecipeNames = newFavs
                            },
                            onAddClick = {
                                val currentCals = PersistenceManager.getMealCalorie("snack")
                                val calValue = recipe.calories.split(" ").firstOrNull()?.toFloatOrNull() ?: 0f
                                PersistenceManager.saveMealCalorie("snack", currentCals + calValue)
                                android.widget.Toast.makeText(context, "${recipe.name} Atıştırmalık öğününe eklendi!", android.widget.Toast.LENGTH_SHORT).show()
                            }
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                    }
                }
            }
        }

        // --- Expandable FAB ---
        Column(
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .padding(16.dp)
                .padding(bottom = 60.dp), // BottomNav padding
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            androidx.compose.animation.AnimatedVisibility(visible = isFabExpanded) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    androidx.compose.material3.SmallFloatingActionButton(
                        onClick = { 
                            isFabExpanded = false
                            isManualInputScreenOpen = true
                        },
                        containerColor = Color.White,
                        contentColor = PrimaryGreen
                    ) {
                        Icon(Icons.Filled.Edit, contentDescription = "Manuel Malzeme Gir")
                    }
                    Spacer(modifier = Modifier.height(12.dp))
                    androidx.compose.material3.SmallFloatingActionButton(
                        onClick = { 
                            isFabExpanded = false
                            cameraLauncher.launch(null)
                        },
                        containerColor = Color.White,
                        contentColor = PrimaryGreen
                    ) {
                        Icon(Icons.Filled.CameraAlt, contentDescription = "Kamera")
                    }
                    Spacer(modifier = Modifier.height(12.dp))
                    androidx.compose.material3.SmallFloatingActionButton(
                        onClick = { 
                            isFabExpanded = false
                            galleryLauncher.launch(PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly))
                        },
                        containerColor = Color.White,
                        contentColor = PrimaryGreen
                    ) {
                        Icon(Icons.Filled.Image, contentDescription = "Galeri")
                    }
                    Spacer(modifier = Modifier.height(16.dp))
                }
            }
            
            FloatingActionButton(
                onClick = { isFabExpanded = !isFabExpanded },
                containerColor = PrimaryGreen,
                contentColor = Color.White,
                shape = CircleShape
            ) {
                Icon(if (isFabExpanded) Icons.Filled.Close else Icons.Filled.AutoAwesome, contentDescription = "Sihirli Şef Asistanı")
            }
        }

        androidx.compose.animation.AnimatedVisibility(
            visible = isManualInputScreenOpen,
            enter = androidx.compose.animation.slideInVertically(initialOffsetY = { it }),
            exit = androidx.compose.animation.slideOutVertically(targetOffsetY = { it })
        ) {
            Box(modifier = Modifier.fillMaxSize().background(Color.White)) {
                Column(modifier = Modifier.fillMaxSize().padding(16.dp).padding(top = 24.dp)) {
                    // Header
                    Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.fillMaxWidth()) {
                        IconButton(onClick = { isManualInputScreenOpen = false }) { Icon(Icons.Filled.Close, contentDescription = "Kapat") }
                        Text("Manuel Malzeme Ekle", fontSize = 20.sp, fontWeight = FontWeight.Bold, color = PrimaryGreen, modifier = Modifier.weight(1f), textAlign = androidx.compose.ui.text.style.TextAlign.Center)
                        Spacer(modifier = Modifier.width(48.dp))
                    }
                    Divider(modifier = Modifier.padding(vertical = 12.dp), color = Color(0xFFEEEEEE))
                    
                    // Input Section
                    Column(modifier = Modifier.fillMaxWidth()) {
                        OutlinedTextField(
                            value = currentIngredient,
                            onValueChange = { currentIngredient = it },
                            label = { Text("Malzeme Girin") },
                            placeholder = { Text("Örn: Domates, Tavuk Göğsü") },
                            modifier = Modifier.fillMaxWidth(),
                            singleLine = true,
                            shape = RoundedCornerShape(12.dp)
                        )
                        Text(
                            text = "💡 İpucu: Lütfen malzemeleri doğru yazdığınızdan emin olun (Örn: 'tavk' yerine 'tavuk').",
                            fontSize = 12.sp,
                            color = Color.Gray,
                            modifier = Modifier.padding(top = 6.dp, start = 4.dp, bottom = 4.dp)
                        )
                    }
                    Spacer(modifier = Modifier.height(12.dp))
                    Button(
                        onClick = {
                            if (currentIngredient.isNotBlank()) {
                                ingredientList = ingredientList + IngredientItem(currentIngredient.trim(), "")
                                currentIngredient = ""
                            }
                        },
                        modifier = Modifier.fillMaxWidth().height(50.dp),
                        shape = RoundedCornerShape(12.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = PrimaryGreen)
                    ) {
                        Icon(Icons.Filled.Add, null)
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Malzeme Ekle", fontWeight = FontWeight.Bold)
                    }
                    
                    Spacer(modifier = Modifier.height(16.dp))
                    Text("Eklenen Malzemeler", fontWeight = FontWeight.Bold, fontSize = 16.sp, color = TextGray)
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    // List Section
                    LazyColumn(modifier = Modifier.weight(1f)) {
                        if (ingredientList.isEmpty()) {
                            item {
                                Box(modifier = Modifier.fillMaxWidth().padding(top = 40.dp), contentAlignment = Alignment.Center) {
                                    Text("Henüz malzeme eklemedin.", color = Color.Gray)
                                }
                            }
                        }
                        items(ingredientList) { item ->
                            Card(
                                modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp), 
                                colors = CardDefaults.cardColors(containerColor = SoftWhite),
                                shape = RoundedCornerShape(12.dp)
                            ) {
                                Row(modifier = Modifier.padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
                                    Icon(Icons.Filled.CheckCircle, null, tint = PrimaryGreen, modifier = Modifier.size(20.dp))
                                    Spacer(modifier = Modifier.width(12.dp))
                                    Text(item.name, fontWeight = FontWeight.Bold, modifier = Modifier.weight(1f))
                                    if (item.amount.isNotBlank()) {
                                        Surface(shape = RoundedCornerShape(6.dp), color = Color.LightGray.copy(alpha = 0.4f)) {
                                            Text(item.amount, fontSize = 12.sp, modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp), color = Color.DarkGray)
                                        }
                                    }
                                    IconButton(onClick = { ingredientList = ingredientList.filter { it != item } }) {
                                        Icon(Icons.Filled.Delete, null, tint = Color.Red.copy(alpha = 0.7f))
                                    }
                                }
                            }
                        }
                    }
                    
                    // Submit Button
                    Button(
                        onClick = {
                            if (ingredientList.isNotEmpty()) {
                                isManualInputScreenOpen = false
                                val textPayload = ingredientList.joinToString(", ") { 
                                    if (it.amount.isNotBlank()) "${it.amount} ${it.name}" else it.name
                                }
                                fetchAiRecipe(null, null, textPayload)
                            }
                        },
                        modifier = Modifier.fillMaxWidth().height(60.dp).padding(bottom = 8.dp),
                        shape = RoundedCornerShape(16.dp),
                        enabled = ingredientList.isNotEmpty(),
                        colors = ButtonDefaults.buttonColors(containerColor = PrimaryGreen)
                    ) {
                        Icon(Icons.Filled.AutoAwesome, null)
                        Spacer(modifier = Modifier.width(12.dp))
                        Text("Şefe Gönder", fontSize = 18.sp, fontWeight = FontWeight.Bold)
                    }
                }
            }
        }
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun RecipeCard(
    recipe: Recipe,
    isFavorite: Boolean = false,
    onFavoriteToggle: (() -> Unit)? = null,
    onAddClick: (() -> Unit)? = null
) {
    var expanded by remember { mutableStateOf(false) }
    Card(modifier = Modifier.fillMaxWidth().clickable { expanded = !expanded }, shape = RoundedCornerShape(20.dp), colors = CardDefaults.cardColors(containerColor = Color.White), elevation = CardDefaults.cardElevation(2.dp)) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                if (recipe.imageRes != null) {
                    coil.compose.AsyncImage(
                        model = recipe.imageRes,
                        contentDescription = null,
                        contentScale = androidx.compose.ui.layout.ContentScale.Crop,
                        modifier = Modifier.size(60.dp).clip(RoundedCornerShape(12.dp))
                    )
                } else {
                    Box(modifier = Modifier.size(44.dp).clip(CircleShape).background(LightGreenBg), contentAlignment = Alignment.Center) { Icon(Icons.Filled.Restaurant, contentDescription = null, tint = PrimaryGreen) }
                }
                Spacer(modifier = Modifier.width(12.dp))
                Column(modifier = Modifier.weight(1f)) {
                    Text(recipe.name, fontWeight = FontWeight.Bold, fontSize = 18.sp, maxLines = 1, overflow = androidx.compose.ui.text.style.TextOverflow.Ellipsis)
                    
                    val calParts = recipe.calories.split("|").map { it.trim() }
                    if (calParts.size > 1) {
                        Text(calParts[0], color = PrimaryGreen, fontSize = 15.sp, fontWeight = FontWeight.Bold)
                        Spacer(modifier = Modifier.height(4.dp))
                        FlowRow(horizontalArrangement = Arrangement.spacedBy(4.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                            for (i in 1 until calParts.size) {
                                Surface(shape = RoundedCornerShape(6.dp), color = SoftWhite, border = BorderStroke(0.5.dp, Color.LightGray)) {
                                    Text(calParts[i], fontSize = 10.sp, color = TextGray, fontWeight = FontWeight.SemiBold, modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp))
                                }
                            }
                        }
                    } else {
                        Text(recipe.calories, color = PrimaryGreen, fontSize = 14.sp, fontWeight = FontWeight.SemiBold)
                    }
                }
                Row(verticalAlignment = Alignment.CenterVertically) {
                    if (onFavoriteToggle != null) {
                        IconButton(onClick = onFavoriteToggle, modifier = Modifier.size(32.dp)) {
                            Icon(Icons.Filled.Star, contentDescription = "Favori", tint = if (isFavorite) Color(0xFFFFC107) else Color(0xFFE0E0E0))
                        }
                    }
                    if (onAddClick != null) {
                        IconButton(onClick = onAddClick, modifier = Modifier.size(32.dp)) {
                            Icon(Icons.Filled.AddCircle, contentDescription = "Kaloriyi Ekle", tint = PrimaryGreen)
                        }
                    }
                    Icon(if (expanded) Icons.Filled.ExpandLess else Icons.Filled.ExpandMore, contentDescription = null, tint = TextGray, modifier = Modifier.padding(start = 4.dp))
                }
            }
            
            Text(recipe.description, fontSize = 14.sp, color = TextGray, modifier = Modifier.padding(top = 12.dp))
            
            if (expanded) {
                Divider(modifier = Modifier.padding(vertical = 16.dp), color = Color(0xFFF0F0F0))
                
                Text(stringResource(R.string.ingredients_label), fontWeight = FontWeight.Bold, color = PrimaryGreen)
                recipe.ingredients.forEach { ing ->
                    Row(modifier = Modifier.padding(vertical = 4.dp), verticalAlignment = Alignment.Top) {
                        Text("• ", color = PrimaryGreen, fontWeight = FontWeight.Bold)
                        Text(ing, fontSize = 14.sp)
                    }
                }
                
                Spacer(modifier = Modifier.height(16.dp))
                
                Text(stringResource(R.string.steps_label), fontWeight = FontWeight.Bold, color = PrimaryGreen)
                recipe.steps.forEachIndexed { index, step ->
                    Row(modifier = Modifier.padding(vertical = 6.dp), verticalAlignment = Alignment.Top) {
                        Text("${index + 1}. ", color = PrimaryGreen, fontWeight = FontWeight.Bold)
                        Text(step, fontSize = 14.sp)
                    }
                }
            }
        }
    }
}

// --- 4. HOME SCREEN ---
@Composable
fun HomeScreen() {
    LazyColumn(modifier = Modifier.fillMaxSize().background(SoftWhite).padding(horizontal = 16.dp), contentPadding = PaddingValues(top = 16.dp, bottom = 80.dp)) {
        item { Row(modifier = Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) { Image(painter = painterResource(id = R.drawable.app_logo), contentDescription = "Profile", modifier = Modifier.size(54.dp).clip(CircleShape)); Spacer(modifier = Modifier.width(12.dp)); Column(modifier = Modifier.weight(1f)) { Text("Merhaba", fontSize = 14.sp, color = TextGray); Text(SessionManager.userName, fontSize = 20.sp, fontWeight = FontWeight.Bold, color = PrimaryGreen) }; Icon(Icons.Filled.Notifications, contentDescription = null, tint = PrimaryGreen) } }
        item { Spacer(modifier = Modifier.height(24.dp)) }
        item {
            Card(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(16.dp), colors = CardDefaults.cardColors(containerColor = Color.White)) {
                Column(modifier = Modifier.padding(20.dp)) {
                    val todayTitle = stringResource(R.string.today_calories_title)
                    var displayCalories by remember { mutableFloatStateOf(0f) }
                    var displayTitle by remember { mutableStateOf(todayTitle) }
                    
                    // Home ekranında günlük toplam gösterilir. Chart'a tıklanınca o gününki gösterilir.
                    androidx.compose.runtime.LaunchedEffect(Unit) {
                        displayCalories = PersistenceManager.getMealCalorie("breakfast") + PersistenceManager.getMealCalorie("lunch") + PersistenceManager.getMealCalorie("dinner") + PersistenceManager.getMealCalorie("snack")
                        displayTitle = todayTitle
                    }
                    
                    Text(displayTitle, fontSize = 18.sp, fontWeight = FontWeight.Bold)
                    Row(verticalAlignment = Alignment.Bottom) {
                        Text("${displayCalories.toInt()}", fontSize = 32.sp, fontWeight = FontWeight.Bold, color = PrimaryGreen)
                        Text(" " + stringResource(R.string.kcal_unit), fontSize = 16.sp, color = TextGray, modifier = Modifier.padding(bottom = 4.dp))
                        Spacer(modifier = Modifier.weight(1f))
                        Text(stringResource(R.string.target_label, PersistenceManager.getTargetCalories().toInt().toString()), fontSize = 14.sp, color = TextGray)
                    }
                    Spacer(modifier = Modifier.height(24.dp))
                    
                    val daySuffix = stringResource(R.string.day_calories_suffix)
                    val daysOptions = listOf(
                        stringResource(R.string.day_mon), stringResource(R.string.day_tue), stringResource(R.string.day_wed),
                        stringResource(R.string.day_thu), stringResource(R.string.day_fri), stringResource(R.string.day_sat), stringResource(R.string.day_sun)
                    )
                    WeeklyBarChart(onBarClick = { index, calories ->
                        displayTitle = daysOptions[index] + daySuffix
                        displayCalories = calories
                    })
                }
            }
        }
        item { Spacer(modifier = Modifier.height(24.dp)) }
        item { Row(Modifier.fillMaxWidth()) { InfoCard(title = "Daily Calorie", value = "${PersistenceManager.getTargetCalories().toInt()} kcal", modifier = Modifier.weight(1f)); Spacer(modifier = Modifier.width(16.dp)); InteractiveWaterCard(modifier = Modifier.weight(1f)) } }
        item { Spacer(modifier = Modifier.height(24.dp)) }
    }
}

// --- 5. CHATBOT SCREEN ---
data class ChatMessage(val text: String, val isFromUser: Boolean)

@Composable
fun ChatbotScreen() {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    val messages = remember { mutableStateListOf(
        ChatMessage(context.getString(R.string.chatbot_welcome_1), false),
        ChatMessage(context.getString(R.string.chatbot_welcome_2), false)
    )}

    Column(modifier = Modifier.fillMaxSize().background(SoftWhite)) {
        LazyColumn(modifier = Modifier.weight(1f).padding(horizontal = 16.dp), reverseLayout = true) {
            item { Spacer(modifier = Modifier.height(8.dp)) }
            items(messages.reversed()) { msg ->
                MessageBubble(msg.text, isFromUser = msg.isFromUser)
            }
            item { Spacer(modifier = Modifier.height(8.dp)) }
        }
        ChatInputBar(onSend = { newMsg ->
            messages.add(ChatMessage(newMsg, true))
            coroutineScope.launch {
                try {
                    val token = SessionManager.token ?: ""
                    val meals = mutableListOf<MealCreate>()
                    val bCal = PersistenceManager.getMealCalorie("breakfast")
                    val lCal = PersistenceManager.getMealCalorie("lunch")
                    val dCal = PersistenceManager.getMealCalorie("dinner")
                    val sCal = PersistenceManager.getMealCalorie("snack")
                    if(bCal > 0f) meals.add(MealCreate("Kahvaltı", bCal))
                    if(lCal > 0f) meals.add(MealCreate("Öğle", lCal))
                    if(dCal > 0f) meals.add(MealCreate("Akşam", dCal))
                    if(sCal > 0f) meals.add(MealCreate("Ara Öğün", sCal))
                    
                    val request = ChatRequest(
                        user_id = SessionManager.userId,
                        user_message = newMsg,
                        history = "",
                        boy_cm = PersistenceManager.boyCm,
                        kilo_kg = PersistenceManager.kiloKg,
                        yas = PersistenceManager.yas,
                        cinsiyet = PersistenceManager.cinsiyet,
                        bugunku_ogunler = meals
                    )
                    
                    val response = RetrofitClient.instance.chatWithAi(token, request)
                    messages.add(ChatMessage(response.reply, false))
                } catch (e: Exception) {
                    messages.add(ChatMessage(context.getString(R.string.chatbot_error, e.localizedMessage ?: ""), false))
                }
            }
        })
    }
}

// --- AUTH EKRANLARI ---

@Composable
fun AuthBackground() {
    Canvas(modifier = Modifier.fillMaxSize().background(SoftWhite)) {
        val width = size.width
        val height = size.height

        val path1 = Path().apply {
            moveTo(0f, 0f)
            lineTo(width * 0.7f, 0f)
            cubicTo(width * 0.3f, height * 0.1f, width * 0.4f, height * 0.25f, 0f, height * 0.35f)
            close()
        }
        drawPath(path1, color = LightGreenBg)

        val path2 = Path().apply {
            moveTo(width, height)
            lineTo(width, height * 0.6f)
            cubicTo(width * 0.6f, height * 0.75f, width * 0.2f, height * 0.8f, 0f, height * 0.95f)
            lineTo(0f, height)
            close()
        }
        drawPath(path2, color = LightGreenBg)
        
        val path3 = Path().apply {
            moveTo(width, height)
            lineTo(width, height * 0.7f)
            cubicTo(width * 0.5f, height * 0.9f, width * 0.1f, height * 0.85f, 0f, height)
            close()
        }
        drawPath(path3, color = LeafGreen.copy(alpha = 0.3f))
    }
}

@Composable
fun LoginScreen(navController: NavController, onLoginSuccess: () -> Unit) {
    var email by remember { mutableStateOf("") }; var password by remember { mutableStateOf("") }
    var isLoading by remember { mutableStateOf(false) }; var errorMessage by remember { mutableStateOf<String?>(null) }
    val coroutineScope = rememberCoroutineScope()

    Box(modifier = Modifier.fillMaxSize()) {
        AuthBackground()
        Column(modifier = Modifier.fillMaxSize().padding(horizontal = 32.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Spacer(modifier = Modifier.height(100.dp)); LogoAndTitle(); Spacer(modifier = Modifier.height(60.dp))
        InputTextField(value = email, onValueChange = { email = it }, label = stringResource(R.string.email_hint))
        Spacer(modifier = Modifier.height(16.dp)); InputTextField(value = password, onValueChange = { password = it }, label = stringResource(R.string.password_hint))
        if (errorMessage != null) Text(errorMessage!!, color = Color.Red, fontSize = 12.sp, modifier = Modifier.padding(top = 8.dp))
        Spacer(modifier = Modifier.height(40.dp))
        Button(
            onClick = {
                isLoading = true
                coroutineScope.launch {
                    try { 
                        val response = RetrofitClient.instance.loginUser(LoginItem(email, password))
                        SessionManager.token = "Bearer ${response.access_token}"
                        SessionManager.userId = response.user_id
                        
                        PersistenceManager.savedToken = SessionManager.token
                        PersistenceManager.savedUserId = SessionManager.userId
                        
                        if (!response.full_name.isNullOrBlank()) {
                            SessionManager.userName = response.full_name
                            PersistenceManager.savedUserName = SessionManager.userName
                        }
                        onLoginSuccess() 
                    }
                    catch (e: retrofit2.HttpException) {
                        if (e.code() == 403 || e.code() == 401) {
                            errorMessage = "E-posta veya şifre hatalı!"
                        } else {
                            errorMessage = "Sunucu Hatası (${e.code()})"
                        }
                    }
                    catch (e: Exception) { errorMessage = "Hata: Sunucuya bağlanılamadı. ${e.localizedMessage}" }
                    finally { isLoading = false }
                }
            },
            modifier = Modifier.fillMaxWidth().height(50.dp), shape = RoundedCornerShape(16.dp), colors = ButtonDefaults.buttonColors(containerColor = PrimaryGreen), enabled = !isLoading
        ) {
            if (isLoading) CircularProgressIndicator(color = Color.White, modifier = Modifier.size(24.dp))
            else Text(text = stringResource(R.string.signin_title), color = Color.White, fontSize = 16.sp)
        }
        Spacer(modifier = Modifier.weight(1f)); SignUpText(onSignUpClick = { navController.navigate(Screen.Register.route) })
        Spacer(modifier = Modifier.height(40.dp))
    }
    }
}

@Composable
fun RegisterScreen(navController: NavController) {
    var fullName by remember { mutableStateOf("") }; var email by remember { mutableStateOf("") }; var password by remember { mutableStateOf("") }
    var isLoading by remember { mutableStateOf(false) }; val coroutineScope = rememberCoroutineScope()

    Box(modifier = Modifier.fillMaxSize()) {
        AuthBackground()
        Column(modifier = Modifier.fillMaxSize().padding(horizontal = 32.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Spacer(modifier = Modifier.height(100.dp)); LogoAndTitle(); Spacer(modifier = Modifier.height(60.dp))
        InputTextField(value = fullName, onValueChange = { fullName = it }, label = stringResource(R.string.full_name_hint))
        Spacer(modifier = Modifier.height(16.dp)); InputTextField(value = email, onValueChange = { email = it }, label = stringResource(R.string.email_hint))
        Spacer(modifier = Modifier.height(16.dp)); InputTextField(value = password, onValueChange = { password = it }, label = stringResource(R.string.password_hint))
        Spacer(modifier = Modifier.height(40.dp))
        Button(
            onClick = {
                if (fullName.isNotBlank() && email.isNotBlank() && password.isNotBlank()) {
                    SessionManager.tempName = fullName
                    SessionManager.tempEmail = email
                    SessionManager.tempPassword = password
                    navController.navigate(Screen.ProfileSetup.route)
                }
            },
            modifier = Modifier.fillMaxWidth().height(50.dp), shape = RoundedCornerShape(16.dp), colors = ButtonDefaults.buttonColors(containerColor = PrimaryGreen)
        ) {
            Text(text = "Devam Et", color = Color.White, fontSize = 16.sp, fontWeight = FontWeight.Bold)
        }
        Spacer(modifier = Modifier.weight(1f)); SignInText(onSignInClick = { navController.navigate(Screen.Login.route) })
        Spacer(modifier = Modifier.height(40.dp))
    }
    }
}

@Composable
fun ProfileSetupScreen(navController: NavController) {
    var boyInput by remember { mutableStateOf("") }
    var kiloInput by remember { mutableStateOf("") }
    var yasInput by remember { mutableStateOf("") }
    var cinsiyetInput by remember { mutableStateOf("") }

    Box(modifier = Modifier.fillMaxSize()) {
        AuthBackground()
        Column(modifier = Modifier.fillMaxSize().padding(horizontal = 32.dp).verticalScroll(rememberScrollState()), horizontalAlignment = Alignment.CenterHorizontally) {
            Spacer(modifier = Modifier.height(80.dp))
            Text("Profilini Tamamla", fontSize = 28.sp, fontWeight = FontWeight.Bold, color = Color.Black)
            Spacer(modifier = Modifier.height(16.dp))
            Text("Sana en uygun kaloriyi hesaplayabilmemiz için bu bilgilere ihtiyacımız var.", fontSize = 14.sp, color = TextGray, textAlign = TextAlign.Center)
            Spacer(modifier = Modifier.height(40.dp))
            
            InputTextField(value = boyInput, onValueChange = { boyInput = it }, label = "Boy (Örn: 175)")
            Spacer(modifier = Modifier.height(16.dp))
            InputTextField(value = kiloInput, onValueChange = { kiloInput = it }, label = "Kilo (Örn: 70)")
            Spacer(modifier = Modifier.height(16.dp))
            InputTextField(value = yasInput, onValueChange = { yasInput = it }, label = "Yaş (Örn: 24)")
            Spacer(modifier = Modifier.height(16.dp))
            
            Column(modifier = Modifier.fillMaxWidth()) {
                Text("Cinsiyet", fontWeight = FontWeight.SemiBold, modifier = Modifier.padding(start = 4.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    RadioButton(selected = cinsiyetInput == "Erkek", onClick = { cinsiyetInput = "Erkek" }, colors = RadioButtonDefaults.colors(selectedColor = PrimaryGreen))
                    Text("Erkek", modifier = Modifier.clickable { cinsiyetInput = "Erkek" })
                    Spacer(modifier = Modifier.width(16.dp))
                    RadioButton(selected = cinsiyetInput == "Kadın", onClick = { cinsiyetInput = "Kadın" }, colors = RadioButtonDefaults.colors(selectedColor = PrimaryGreen))
                    Text("Kadın", modifier = Modifier.clickable { cinsiyetInput = "Kadın" })
                }
            }
            Spacer(modifier = Modifier.height(40.dp))
            
            Button(
                onClick = {
                    if (boyInput.isNotBlank() && kiloInput.isNotBlank() && yasInput.isNotBlank() && cinsiyetInput.isNotBlank()) {
                        SessionManager.tempBoy = boyInput.toFloatOrNull() ?: 170.0f
                        SessionManager.tempKilo = kiloInput.toFloatOrNull() ?: 70.0f
                        SessionManager.tempYas = yasInput.toIntOrNull() ?: 30
                        SessionManager.tempCinsiyet = cinsiyetInput
                        navController.navigate(Screen.ActivityLevel.route)
                    }
                },
                modifier = Modifier.fillMaxWidth().height(50.dp),
                shape = RoundedCornerShape(16.dp),
                colors = ButtonDefaults.buttonColors(containerColor = PrimaryGreen)
            ) {
                Text("İleri", color = Color.White, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            }
            Spacer(modifier = Modifier.height(40.dp))
        }
    }
}

@Composable
fun ActivityLevelScreen(navController: NavController) {
    var selectedLevel by remember { mutableStateOf("Hareketsiz") }
    var isLoading by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    val coroutineScope = rememberCoroutineScope()
    val context = LocalContext.current

    val activities = listOf(
        Pair("Hareketsiz", "Günümün çoğu oturarak geçiyor\nSpor yapmıyorum\n0–5.000 adım"),
        Pair("Az Aktif", "Hafif hareketli geçiyor\nHaftada 1-2 gün hafif egzersiz\n5.000–8.000 adım"),
        Pair("Orta Aktif", "Hareketli bir yaşantım var\nHaftada 3-4 gün spor yapıyorum\n8.000–12.000 adım"),
        Pair("Çok Aktif", "Sürekli hareket halindeyim\nHer gün ağır idman yapıyorum\n12.000+ adım")
    )

    Box(modifier = Modifier.fillMaxSize()) {
        AuthBackground()
        Column(modifier = Modifier.fillMaxSize().padding(horizontal = 24.dp).verticalScroll(rememberScrollState()), horizontalAlignment = Alignment.CenterHorizontally) {
            Spacer(modifier = Modifier.height(80.dp))
            Text("Ne Kadar Hareketlisin?", fontSize = 26.sp, fontWeight = FontWeight.Bold, color = Color.Black)
            Spacer(modifier = Modifier.height(12.dp))
            Text("Sana uygun kalori hedefini belirlememiz için hareket seviyeni seç.", fontSize = 14.sp, color = TextGray, textAlign = TextAlign.Center)
            Spacer(modifier = Modifier.height(30.dp))

            activities.forEach { (level, desc) ->
                val isSelected = selectedLevel == level
                Card(
                    modifier = Modifier.fillMaxWidth().height(90.dp).clickable { selectedLevel = level },
                    shape = RoundedCornerShape(16.dp),
                    border = BorderStroke(1.dp, if (isSelected) PrimaryGreen else Color.Transparent),
                    colors = CardDefaults.cardColors(containerColor = if (isSelected) LightGreenBg else Color.White),
                    elevation = CardDefaults.cardElevation(if (isSelected) 4.dp else 1.dp)
                ) {
                    Row(modifier = Modifier.fillMaxSize().padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
                        RadioButton(selected = isSelected, onClick = { selectedLevel = level }, colors = RadioButtonDefaults.colors(selectedColor = PrimaryGreen))
                        Spacer(modifier = Modifier.width(8.dp))
                        Column(modifier = Modifier.weight(1f)) {
                            Text(level, fontWeight = FontWeight.Bold, fontSize = 16.sp, color = if (isSelected) PrimaryGreen else Color.Black)
                            Text(desc, fontSize = 12.sp, color = TextGray, lineHeight = 16.sp)
                        }
                    }
                }
                Spacer(modifier = Modifier.height(12.dp))
            }

            if (errorMessage != null) {
                Text(errorMessage!!, color = Color.Red, fontSize = 12.sp, modifier = Modifier.padding(top = 8.dp))
            }
            Spacer(modifier = Modifier.height(20.dp))

            Button(
                onClick = {
                    SessionManager.tempActivityLevel = selectedLevel
                    navController.navigate(Screen.GoalSetup.route)
                },
                modifier = Modifier.fillMaxWidth().height(50.dp),
                shape = RoundedCornerShape(16.dp),
                colors = ButtonDefaults.buttonColors(containerColor = PrimaryGreen)
            ) {
                Text("İleri", color = Color.White, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            }
            Spacer(modifier = Modifier.height(40.dp))
        }
    }
}

@Composable
fun GoalSetupScreen(navController: NavController) {
    var selectedGoal by remember { mutableStateOf("Kilo Vermek") }
    var targetWeight by remember { mutableStateOf("") }
    
    // Hız seçimi için Slider durumları (Sadece Vermek ve Almak için geçerli)
    var loseSpeedIndex by remember { mutableStateOf(1f) } // 0:Yavaş, 1:İdeal, 2:Agresif
    var gainSpeedIndex by remember { mutableStateOf(0f) } // 0:Kas Odaklı, 1:Hızlı Kilo
    
    var isLoading by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    val coroutineScope = rememberCoroutineScope()
    val context = LocalContext.current

    val goals = listOf("Kilo Vermek", "Kilo Almak", "Korumak")

    Box(modifier = Modifier.fillMaxSize()) {
        AuthBackground()
        Column(modifier = Modifier.fillMaxSize().padding(horizontal = 24.dp).verticalScroll(rememberScrollState()), horizontalAlignment = Alignment.CenterHorizontally) {
            Spacer(modifier = Modifier.height(80.dp))
            Text("Son Olarak Hedefin Nedir?", fontSize = 24.sp, fontWeight = FontWeight.Bold, color = Color.Black)
            Spacer(modifier = Modifier.height(12.dp))
            Text("Sana özel kalori ve makro profilini oluşturmamız için amacını bilmeliyiz.", fontSize = 14.sp, color = TextGray, textAlign = TextAlign.Center)
            Spacer(modifier = Modifier.height(30.dp))

            goals.forEach { goal ->
                val isSelected = selectedGoal == goal
                Card(
                    modifier = Modifier.fillMaxWidth().height(60.dp).clickable { selectedGoal = goal },
                    shape = RoundedCornerShape(16.dp),
                    border = BorderStroke(1.dp, if (isSelected) PrimaryGreen else Color.Transparent),
                    colors = CardDefaults.cardColors(containerColor = if (isSelected) LightGreenBg else Color.White)
                ) {
                    Row(modifier = Modifier.fillMaxSize().padding(horizontal = 16.dp), verticalAlignment = Alignment.CenterVertically) {
                        RadioButton(selected = isSelected, onClick = { selectedGoal = goal }, colors = RadioButtonDefaults.colors(selectedColor = PrimaryGreen))
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(goal, fontWeight = FontWeight.Bold, fontSize = 16.sp, color = if (isSelected) PrimaryGreen else Color.Black)
                    }
                }
                Spacer(modifier = Modifier.height(12.dp))
            }

            Spacer(modifier = Modifier.height(14.dp))

            if (selectedGoal != "Korumak") {
                InputTextField(value = targetWeight, onValueChange = { targetWeight = it }, label = "Hedef Kilo (Örn: 65)")
                Spacer(modifier = Modifier.height(24.dp))
                
                Text("Hız ve Tempon:", fontWeight = FontWeight.SemiBold)
                Spacer(modifier = Modifier.height(8.dp))
                
                if (selectedGoal == "Kilo Vermek") {
                    androidx.compose.material3.Slider(
                        value = loseSpeedIndex,
                        onValueChange = { loseSpeedIndex = it },
                        valueRange = 0f..2f,
                        steps = 1,
                        colors = androidx.compose.material3.SliderDefaults.colors(thumbColor = PrimaryGreen, activeTrackColor = PrimaryGreen)
                    )
                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        Text("Yavaş (-0.25)", fontSize = 12.sp, color = if(loseSpeedIndex==0f) PrimaryGreen else TextGray)
                        Text("İdeal (-0.5)", fontSize = 12.sp, color = if(loseSpeedIndex==1f) PrimaryGreen else TextGray)
                        Text("Agresif (-1.0)", fontSize = 12.sp, color = if(loseSpeedIndex==2f) PrimaryGreen else TextGray)
                    }
                } else if (selectedGoal == "Kilo Almak") {
                    androidx.compose.material3.Slider(
                        value = gainSpeedIndex,
                        onValueChange = { gainSpeedIndex = it },
                        valueRange = 0f..1f,
                        steps = 0,
                        colors = androidx.compose.material3.SliderDefaults.colors(thumbColor = PrimaryGreen, activeTrackColor = PrimaryGreen)
                    )
                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        Text("Kas Odaklı (Yavaş)", fontSize = 12.sp, color = if(gainSpeedIndex==0f) PrimaryGreen else TextGray)
                        Text("Hızlı Kilo", fontSize = 12.sp, color = if(gainSpeedIndex==1f) PrimaryGreen else TextGray)
                    }
                }
                Spacer(modifier = Modifier.height(16.dp))
            }

            if (errorMessage != null) {
                Text(errorMessage!!, color = Color.Red, fontSize = 12.sp, modifier = Modifier.padding(top = 8.dp))
            }
            Spacer(modifier = Modifier.height(24.dp))

            Button(
                onClick = {
                    val floatTarget = targetWeight.toFloatOrNull() ?: 0f
                    if (selectedGoal == "Kilo Vermek" && floatTarget >= SessionManager.tempKilo) {
                        errorMessage = "Hata: Kilo vermek için hedef kilonuz mevcut kilonuzdan (${SessionManager.tempKilo}) küçük olmalıdır."
                        return@Button
                    }
                    if (selectedGoal == "Kilo Almak" && floatTarget <= SessionManager.tempKilo) {
                        errorMessage = "Hata: Kilo almak için hedef kilonuz mevcut kilonuzdan (${SessionManager.tempKilo}) büyük olmalıdır."
                        return@Button
                    }
                    if (selectedGoal != "Korumak" && floatTarget <= 0f) {
                        errorMessage = "Hata: Lütfen geçerli bir hedef kilo giriniz."
                        return@Button
                    }

                    val finalSpeed = if (selectedGoal == "Kilo Vermek") {
                        when (loseSpeedIndex) {
                            0f -> "0.25 (Yavaş)"
                            1f -> "0.5 (İdeal)"
                            else -> "1.0 (Agresif)"
                        }
                    } else if (selectedGoal == "Kilo Almak") {
                        when (gainSpeedIndex) {
                            0f -> "Kas Odaklı"
                            else -> "Hızlı"
                        }
                    } else "Korumak"

                    SessionManager.tempHedef = selectedGoal
                    SessionManager.tempHedefHiz = if(selectedGoal == "Korumak") "" else finalSpeed
                    SessionManager.tempHedefKilo = floatTarget
                    navController.navigate(Screen.DietarySetup.route)
                },
                modifier = Modifier.fillMaxWidth().height(50.dp),
                shape = RoundedCornerShape(16.dp),
                colors = ButtonDefaults.buttonColors(containerColor = PrimaryGreen)
            ) {
                Text("İleri", color = Color.White, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            }
            Spacer(modifier = Modifier.height(40.dp))
        }
    }
}

@Composable
fun DietarySetupScreen(navController: NavController, onSetupComplete: () -> Unit) {
    var isLoading by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    val coroutineScope = rememberCoroutineScope()
    val context = LocalContext.current

    val restrictions = listOf(
        "Diyabet (Şeker Kısıtlı)",
        "Hipertansiyon (Tuz Kısıtlı)",
        "Laktoz İntoleransı",
        "Gluten Hassasiyeti",
        "Vegan / Vejetaryen"
    )
    
    // Checkbox durumlarını tutan map
    val checkedStates = remember { mutableStateMapOf<String, Boolean>().apply {
        restrictions.forEach { this[it] = false }
    }}

    Box(modifier = Modifier.fillMaxSize()) {
        AuthBackground()
        Column(modifier = Modifier.fillMaxSize().padding(horizontal = 24.dp).verticalScroll(rememberScrollState()), horizontalAlignment = Alignment.CenterHorizontally) {
            Spacer(modifier = Modifier.height(80.dp))
            Text("Diyet Kısıtlamaların", fontSize = 24.sp, fontWeight = FontWeight.Bold, color = Color.Black)
            Spacer(modifier = Modifier.height(12.dp))
            Text("Sana uygun tarifleri ve öğünleri sunabilmemiz için rahatsızlıklarını veya diyet seçimini işaretle. (İsteğe Bağlı)", fontSize = 14.sp, color = TextGray, textAlign = TextAlign.Center)
            Spacer(modifier = Modifier.height(30.dp))

            restrictions.forEach { restriction ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(56.dp)
                        .clickable { checkedStates[restriction] = !(checkedStates[restriction] ?: false) }
                        .padding(horizontal = 16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    androidx.compose.material3.Checkbox(
                        checked = checkedStates[restriction] ?: false,
                        onCheckedChange = { isChecked -> checkedStates[restriction] = isChecked },
                        colors = androidx.compose.material3.CheckboxDefaults.colors(checkedColor = PrimaryGreen)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(text = restriction, fontSize = 16.sp, color = Color.Black)
                }
                androidx.compose.material3.Divider(color = Color.LightGray.copy(alpha = 0.5f), thickness = 1.dp)
            }

            Spacer(modifier = Modifier.height(24.dp))

            if (errorMessage != null) {
                Text(errorMessage!!, color = Color.Red, fontSize = 12.sp, modifier = Modifier.padding(top = 8.dp))
            }
            Spacer(modifier = Modifier.height(24.dp))

            Button(
                onClick = {
                    val selectedRestrictions = checkedStates.filter { it.value }.keys.joinToString(", ")
                    SessionManager.tempDietary = selectedRestrictions
                    
                    isLoading = true
                    coroutineScope.launch {
                        try {
                            val userPayload = UserCreate(
                                email = SessionManager.tempEmail,
                                password = SessionManager.tempPassword,
                                full_name = SessionManager.tempName.takeIf { it.isNotBlank() },
                                boy_cm = SessionManager.tempBoy,
                                kilo_kg = SessionManager.tempKilo,
                                yas = SessionManager.tempYas,
                                cinsiyet = SessionManager.tempCinsiyet.takeIf { it.isNotBlank() } ?: "Belirtilmemiş",
                                activity_level = SessionManager.tempActivityLevel.takeIf { it.isNotBlank() } ?: "Hareketsiz",
                                hedef = SessionManager.tempHedef,
                                hedef_hiz = SessionManager.tempHedefHiz.takeIf { it.isNotBlank() },
                                hedef_kilo = SessionManager.tempHedefKilo,
                                dietary_restrictions = selectedRestrictions.takeIf { it.isNotBlank() }
                            )
                            RetrofitClient.instance.registerUser(userPayload)
                            
                            val loginResponse = RetrofitClient.instance.loginUser(LoginItem(SessionManager.tempEmail, SessionManager.tempPassword))
                            SessionManager.token = "Bearer ${loginResponse.access_token}"
                            SessionManager.userId = loginResponse.user_id
                            SessionManager.userName = loginResponse.full_name ?: SessionManager.tempName

                            PersistenceManager.init(context)
                            PersistenceManager.savedToken = SessionManager.token
                            PersistenceManager.savedUserId = SessionManager.userId
                            PersistenceManager.savedUserName = SessionManager.userName
                            
                            PersistenceManager.boyCm = SessionManager.tempBoy
                            PersistenceManager.kiloKg = SessionManager.tempKilo
                            PersistenceManager.yas = SessionManager.tempYas
                            PersistenceManager.cinsiyet = SessionManager.tempCinsiyet.takeIf { it.isNotBlank() } ?: "Belirtilmemiş"
                            PersistenceManager.activityLevel = SessionManager.tempActivityLevel.takeIf { it.isNotBlank() } ?: "Hareketsiz"
                            PersistenceManager.hedef = SessionManager.tempHedef
                            PersistenceManager.hedefHiz = SessionManager.tempHedefHiz
                            PersistenceManager.hedefKilo = SessionManager.tempHedefKilo
                            PersistenceManager.dietaryRestrictions = selectedRestrictions

                            onSetupComplete()
                        } catch (e: Exception) {
                            errorMessage = "Hata: ${e.localizedMessage}"
                        } finally {
                            isLoading = false
                        }
                    }
                },
                modifier = Modifier.fillMaxWidth().height(50.dp),
                shape = RoundedCornerShape(16.dp),
                colors = ButtonDefaults.buttonColors(containerColor = PrimaryGreen),
                enabled = !isLoading
            ) {
                if (isLoading) CircularProgressIndicator(color = Color.White, modifier = Modifier.size(24.dp))
                else Text("Kayıt Ol", color = Color.White, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            }
            Spacer(modifier = Modifier.height(40.dp))
        }
    }
}

// --- TÜM YARDIMCI COMPOSABLE'LAR ---

@Composable
fun LogoAndTitle() { Image(painter = painterResource(id = R.drawable.app_logo), contentDescription = null, modifier = Modifier.size(100.dp)); Spacer(modifier = Modifier.height(16.dp)); Text(text = "Calorie Calculator", fontSize = 28.sp, fontWeight = FontWeight.Bold, color = Color.Black) }
@Composable
fun InputTextField(value: String, onValueChange: (String) -> Unit, label: String) { OutlinedTextField(value = value, onValueChange = onValueChange, label = { Text(text = label) }, shape = RoundedCornerShape(16.dp), singleLine = true, modifier = Modifier.fillMaxWidth(), colors = OutlinedTextFieldDefaults.colors(focusedBorderColor = PrimaryGreen, unfocusedBorderColor = Color.LightGray)) }
@Composable
fun SignUpText(onSignUpClick: () -> Unit) { Row { Text(text = stringResource(R.string.no_account), color = TextGray); Text(text = stringResource(R.string.signup_title), color = PrimaryGreen, fontWeight = FontWeight.Bold, modifier = Modifier.clickable { onSignUpClick() }) } }
@Composable
fun SignInText(onSignInClick: () -> Unit) { Row { Text(text = stringResource(R.string.have_account), color = TextGray); Text(text = stringResource(R.string.signin_title), color = PrimaryGreen, fontWeight = FontWeight.Bold, modifier = Modifier.clickable { onSignInClick() }) } }
@Composable
fun InfoCard(title: String, value: String, modifier: Modifier) { Card(modifier = modifier.height(110.dp), shape = RoundedCornerShape(24.dp), colors = CardDefaults.cardColors(containerColor = LightGreenBg), elevation = CardDefaults.cardElevation(defaultElevation = 0.dp)) { Column(modifier = Modifier.fillMaxSize().padding(16.dp), verticalArrangement = Arrangement.Center, horizontalAlignment = Alignment.CenterHorizontally) { Text(title, color = TextGray, fontSize = 14.sp); Spacer(modifier=Modifier.height(8.dp)); Text(value, fontWeight = FontWeight.Bold, fontSize = 22.sp, color = PrimaryGreen) } } }

@Composable
fun InteractiveWaterCard(modifier: Modifier) {
    var waterGlasses by remember { mutableIntStateOf(0) }
    var isLoading by remember { mutableStateOf(false) }
    val coroutineScope = rememberCoroutineScope()
    
    Card(modifier = modifier.height(110.dp).clickable {
        if (isLoading) return@clickable
        waterGlasses++
        isLoading = true
        coroutineScope.launch {
            try {
                val token = SessionManager.token ?: ""
                if (token.isNotEmpty()) {
                    RetrofitClient.instance.addWater(token, WaterCreate(250)) // Dila'nın istediği 250ml
                }
            } catch (e: Exception) {
                // Hata durumunda bardağı geri alabiliriz ama şimdilik yoksayıyoruz.
            } finally {
                isLoading = false
            }
        }
    }, shape = RoundedCornerShape(24.dp), colors = CardDefaults.cardColors(containerColor = LightGreenBg), elevation = CardDefaults.cardElevation(defaultElevation = 0.dp)) { 
        Row(modifier = Modifier.fillMaxSize().padding(16.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.Center) { 
            Column(modifier = Modifier.weight(1f), verticalArrangement = Arrangement.Center, horizontalAlignment = Alignment.CenterHorizontally) { 
                Text("Drink Water", color = TextGray, fontSize = 14.sp)
                Spacer(modifier=Modifier.height(8.dp))
                Text("$waterGlasses glass", fontWeight = FontWeight.Bold, fontSize = 20.sp, color = PrimaryGreen) 
            }
            if (isLoading) {
                CircularProgressIndicator(modifier = Modifier.size(20.dp), color = PrimaryGreen, strokeWidth = 2.dp)
            } else {
                Box(modifier = Modifier.size(28.dp).clip(CircleShape).background(PrimaryGreen.copy(alpha=0.2f)), contentAlignment = Alignment.Center) {
                    Icon(Icons.Filled.Add, contentDescription = "Add Water", tint = PrimaryGreen, modifier = Modifier.size(16.dp))
                }
            }
        } 
    } 
}
@Composable
fun MealCard(mealType: String, calorieRange: String) { Card(modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp), shape = RoundedCornerShape(24.dp), colors = CardDefaults.cardColors(containerColor = Color.White), elevation = CardDefaults.cardElevation(2.dp)) { Row(modifier = Modifier.padding(18.dp), verticalAlignment = Alignment.CenterVertically) { Box(modifier = Modifier.size(40.dp).clip(CircleShape).background(LightGreenBg), contentAlignment = Alignment.Center) { Icon(Icons.Filled.Restaurant, contentDescription = null, tint = PrimaryGreen) }; Spacer(modifier = Modifier.width(16.dp)); Column(modifier = Modifier.weight(1f)) { Text(mealType, fontWeight = FontWeight.Bold, fontSize = 16.sp, color = Color(0xFF222222)); Text(calorieRange, color = TextGray, fontSize = 14.sp) } } } }

@Composable
fun InteractiveMealCard(mealType: String, calorieRange: String, onAddManualCalorie: () -> Unit) { 
    Card(modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp), shape = RoundedCornerShape(24.dp), colors = CardDefaults.cardColors(containerColor = Color.White), elevation = CardDefaults.cardElevation(2.dp)) { 
        Row(modifier = Modifier.padding(18.dp), verticalAlignment = Alignment.CenterVertically) { 
            Box(modifier = Modifier.size(40.dp).clip(CircleShape).background(LightGreenBg), contentAlignment = Alignment.Center) { Icon(Icons.Filled.Restaurant, contentDescription = null, tint = PrimaryGreen) }
            Spacer(modifier = Modifier.width(16.dp))
            Column(modifier = Modifier.weight(1f)) { Text(mealType, fontWeight = FontWeight.Bold, fontSize = 16.sp, color = Color(0xFF222222)); Text(calorieRange, color = TextGray, fontSize = 14.sp) }
            IconButton(onClick = onAddManualCalorie) { Icon(Icons.Filled.AddCircle, contentDescription = null, tint = PrimaryGreen, modifier = Modifier.size(28.dp)) } 
        } 
    } 
}
@Composable
fun MessageBubble(text: String, isFromUser: Boolean) { Row(modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp), horizontalArrangement = if (isFromUser) Arrangement.End else Arrangement.Start) { Card(shape = RoundedCornerShape(topStart = 16.dp, topEnd = 16.dp, bottomStart = if (isFromUser) 16.dp else 0.dp, bottomEnd = if (isFromUser) 0.dp else 16.dp), colors = CardDefaults.cardColors(containerColor = if (isFromUser) PrimaryGreen else Color(0xFFEFEFEF))) { Text(text = text, color = if (isFromUser) Color.White else Color.Black, modifier = Modifier.padding(horizontal = 16.dp, vertical = 10.dp)) } } }
@Composable
fun ChatInputBar(onSend: (String) -> Unit) { var inputText by remember { mutableStateOf("") }; Card(modifier = Modifier.fillMaxWidth(), elevation = CardDefaults.cardElevation(8.dp)) { Row(modifier = Modifier.background(Color.White).padding(horizontal = 16.dp, vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) { OutlinedTextField(value = inputText, onValueChange = { inputText = it }, label = { Text(stringResource(R.string.chatbot_hint)) }, modifier = Modifier.weight(1f), shape = RoundedCornerShape(24.dp), colors = OutlinedTextFieldDefaults.colors(focusedBorderColor = PrimaryGreen, unfocusedBorderColor = Color.LightGray)); Spacer(modifier = Modifier.width(8.dp)); IconButton(onClick = { if (inputText.isNotBlank()) { onSend(inputText); inputText = "" } }, modifier = Modifier.size(48.dp).clip(CircleShape).background(PrimaryGreen)) { Icon(Icons.AutoMirrored.Filled.Send, contentDescription = null, tint = Color.White) } } } }
@Composable
fun SettingsSection(title: String) { Text(text = title, color = PrimaryGreen, fontWeight = FontWeight.Bold, modifier = Modifier.padding(bottom = 8.dp)) }
@Composable
fun SettingsItem(title: String, subtitle: String? = null, icon: ImageVector, onClick: () -> Unit = {}) { Card(modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp).clickable(onClick = onClick), shape = RoundedCornerShape(16.dp), colors = CardDefaults.cardColors(containerColor = Color.White)) { Row(modifier = Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically) { Icon(imageVector = icon, contentDescription = null, tint = TextGray); Spacer(modifier = Modifier.width(16.dp)); Column(modifier = Modifier.weight(1f)) { Text(title, fontWeight = FontWeight.SemiBold); if (subtitle != null) Text(subtitle, fontSize = 12.sp, color = TextGray) }; Icon(imageVector = Icons.AutoMirrored.Filled.ArrowForwardIos, contentDescription = null, tint = TextGray, modifier = Modifier.size(16.dp)) } } }
@Composable
fun OnboardingPage(navController: NavController, @DrawableRes imageResId: Int, title: String, description: String, nextRoute: String) { Box(modifier = Modifier.fillMaxSize()) { Image(painter = painterResource(id = imageResId), contentDescription = null, modifier = Modifier.fillMaxSize(), contentScale = ContentScale.Crop); Box(modifier = Modifier.fillMaxSize().background(Brush.verticalGradient(colors = listOf(Color.Transparent, PrimaryGreen.copy(alpha = 0.5f), PrimaryGreen), startY = 600f))); Column(modifier = Modifier.fillMaxSize().padding(horizontal = 32.dp).padding(bottom = 60.dp), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Bottom) { Text(text = title, fontSize = 24.sp, fontWeight = FontWeight.Bold, color = Color.White); Spacer(modifier = Modifier.height(16.dp)); Text(text = description, fontSize = 16.sp, color = Color.White.copy(alpha = 0.8f), textAlign = TextAlign.Center); Spacer(modifier = Modifier.height(40.dp)); Button(onClick = { navController.navigate(nextRoute) }, modifier = Modifier.fillMaxWidth().height(50.dp), shape = RoundedCornerShape(16.dp), colors = ButtonDefaults.buttonColors(containerColor = Color.White)) { Text(text = "NEXT", color = PrimaryGreen, fontWeight = FontWeight.Bold) } } } }
@Composable
fun WelcomeScreen(navController: NavController) { Box(modifier = Modifier.fillMaxSize()) { AuthBackground(); Column(modifier = Modifier.fillMaxSize().padding(horizontal = 32.dp), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) { LogoAndTitle(); Spacer(modifier = Modifier.height(100.dp)); Button(onClick = { navController.navigate(Screen.Login.route) }, modifier = Modifier.fillMaxWidth().height(50.dp), shape = RoundedCornerShape(16.dp), colors = ButtonDefaults.buttonColors(containerColor = PrimaryGreen)) { Text(text = "SIGN IN", color = Color.White) }; Spacer(modifier = Modifier.height(16.dp)); OutlinedButton(onClick = { navController.navigate(Screen.Register.route) }, modifier = Modifier.fillMaxWidth().height(50.dp), shape = RoundedCornerShape(16.dp), border = BorderStroke(1.dp, PrimaryGreen)) { Text(text = "SIGN UP", color = PrimaryGreen) } } } }
@Composable
fun WeeklyBarChart(onBarClick: (Int, Float) -> Unit) {
    val maxCalorieGoal = 2500f
    val days = listOf(
        stringResource(R.string.day_mon), stringResource(R.string.day_tue), stringResource(R.string.day_wed),
        stringResource(R.string.day_thu), stringResource(R.string.day_fri), stringResource(R.string.day_sat), stringResource(R.string.day_sun)
    )
    
    // Geçmiş istatistikleri çek (0: Pazartesi -> 6: Pazar)
    val weeklyData = remember { FloatArray(7) { i -> PersistenceManager.getHistory(i) } }

    Row(modifier = Modifier.fillMaxWidth().height(150.dp), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.Bottom) {
        weeklyData.forEachIndexed { index, calories -> 
            val percentage = (calories / maxCalorieGoal).coerceIn(0f, 1f)
            val isToday = index == ((java.util.Calendar.getInstance().get(java.util.Calendar.DAY_OF_WEEK) + 5) % 7)
            
            Column(horizontalAlignment = Alignment.CenterHorizontally, modifier = Modifier.clickable { onBarClick(index, calories) }) { 
                Box(modifier = Modifier.width(20.dp).fillMaxHeight(percentage.coerceAtLeast(0.02f)).clip(RoundedCornerShape(6.dp)).background(if (isToday) LeafGreen else LeafGreen.copy(alpha = 0.3f)))
                Spacer(modifier = Modifier.height(4.dp))
                Text(days[index], fontSize = 12.sp, color = if (isToday) PrimaryGreen else TextGray, fontWeight = if (isToday) FontWeight.Bold else FontWeight.Normal) 
            } 
        }
    }
}
@Composable
fun StatisticInfoCard(title: String, value: String, icon: ImageVector, color: Color, modifier: Modifier = Modifier) {
    Card(modifier = modifier, shape = RoundedCornerShape(20.dp), colors = CardDefaults.cardColors(containerColor = Color.White)) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) { Box(modifier = Modifier.size(40.dp).clip(CircleShape).background(color.copy(alpha = 0.1f)), contentAlignment = Alignment.Center) { Icon(imageVector = icon, contentDescription = null, tint = color) }; Spacer(modifier = Modifier.width(8.dp)); Text(title, fontSize = 14.sp, color = TextGray) }
            Spacer(modifier = Modifier.height(16.dp)); Text(value, fontSize = 20.sp, fontWeight = FontWeight.Bold); Spacer(modifier = Modifier.height(8.dp)); Canvas(modifier = Modifier.fillMaxWidth().height(30.dp)) {
            val path = Path(); path.moveTo(0f, size.height * 0.5f); path.lineTo(size.width * 0.2f, size.height * 0.8f); path.lineTo(size.width * 0.4f, size.height * 0.2f); path.lineTo(size.width * 0.6f, size.height * 0.6f); path.lineTo(size.width, size.height * 0.7f); drawPath(path = path, color = color, style = Stroke(width = 4f))
        }
    }
}
}