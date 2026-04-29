import re
import sys

with open('CalorieCalculator/app/src/main/java/com/example/caloriecalculator/MainActivity.kt', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update AppBottomBar definition and its Calculate button
content = re.sub(
    r'fun AppBottomBar\(navController: NavController\) \{',
    r'fun AppBottomBar(navController: NavController, onCalculateClick: () -> Unit) {',
    content
)

content = re.sub(
    r'NavigationBarItem\(icon = \{ Icon\(Icons.Filled.CameraAlt, stringResource\(R.string.nav_calculate\)\) \}, label = \{ Text\(stringResource\(R.string.nav_calculate\), fontWeight = FontWeight.Medium\) \}, selected = currentRoute == Screen.Calculate.route, onClick = \{ navController.navigate\(Screen.Calculate.route\) \}, colors = colors\)',
    r'NavigationBarItem(icon = { Icon(Icons.Filled.CameraAlt, stringResource(R.string.nav_calculate)) }, label = { Text(stringResource(R.string.nav_calculate), fontWeight = FontWeight.Medium) }, selected = false, onClick = { onCalculateClick() }, colors = colors)',
    content
)

# 2. Update MainScaffold
scaffold_search = r'val navController = androidx\.navigation\.compose\.rememberNavController\(\)\n    Scaffold\(\n        bottomBar = \{ AppBottomBar\(navController = navController\) \}\n    \) \{ paddingValues ->\n        NavHost\(navController = navController, startDestination = Screen\.Home\.route, Modifier\.padding\(paddingValues\)\) \{'

scaffold_replace = r'''    var isCalculateMenuOpen by remember { mutableStateOf(false) }
    val navController = androidx.navigation.compose.rememberNavController()
    Scaffold(
        bottomBar = { AppBottomBar(navController = navController, onCalculateClick = { isCalculateMenuOpen = !isCalculateMenuOpen }) }
    ) { paddingValues ->
        Box(modifier = Modifier.fillMaxSize()) {
            NavHost(navController = navController, startDestination = Screen.Home.route, Modifier.padding(paddingValues)) {'''

content = re.sub(scaffold_search, scaffold_replace, content)

# Remove the composable(Screen.Calculate.route) inside NavHost
content = re.sub(r'composable\(Screen\.Calculate\.route\) \{ CalculateScreen\(\) \}\n\s*', '', content)

# Add the FAB overlay at the end of NavHost before MainScaffold closes
navhost_end_search = r'            composable\(Screen\.Settings\.route\) \{ SettingsScreen\(navController, onLogout\) \}\n        \}\n    \}\n\}'

navhost_end_replace = r'''            composable(Screen.Settings.route) { SettingsScreen(navController, onLogout) }
            }

            if (isCalculateMenuOpen) {
                Box(modifier = Modifier.fillMaxSize().background(Color.Black.copy(alpha = 0.4f)).clickable(
                    interactionSource = remember { androidx.compose.foundation.interaction.MutableInteractionSource() },
                    indication = null,
                    onClick = { isCalculateMenuOpen = false }
                )) {
                    val expandProgress by androidx.compose.animation.core.animateFloatAsState(
                        targetValue = if (isCalculateMenuOpen) 1f else 0f,
                        animationSpec = androidx.compose.animation.core.tween(300)
                    )
                    
                    Box(modifier = Modifier.align(Alignment.BottomCenter).padding(bottom = 90.dp), contentAlignment = Alignment.Center) {
                        // Manuel
                        androidx.compose.material3.SmallFloatingActionButton(
                            onClick = { isCalculateMenuOpen = false },
                            containerColor = Color(0xFFDCFCE7),
                            contentColor = PrimaryGreen,
                            modifier = Modifier.offset(x = (-100 * expandProgress).dp, y = (-20 * expandProgress).dp).alpha(expandProgress)
                        ) { Icon(Icons.Filled.Edit, "Manuel") }

                        // Kamera
                        androidx.compose.material3.SmallFloatingActionButton(
                            onClick = { isCalculateMenuOpen = false },
                            containerColor = Color(0xFFDCFCE7),
                            contentColor = PrimaryGreen,
                            modifier = Modifier.offset(x = (-40 * expandProgress).dp, y = (-80 * expandProgress).dp).alpha(expandProgress)
                        ) { Icon(Icons.Filled.CameraAlt, "Kamera") }

                        // Galeri
                        androidx.compose.material3.SmallFloatingActionButton(
                            onClick = { isCalculateMenuOpen = false },
                            containerColor = Color(0xFFDCFCE7),
                            contentColor = PrimaryGreen,
                            modifier = Modifier.offset(x = (40 * expandProgress).dp, y = (-80 * expandProgress).dp).alpha(expandProgress)
                        ) { Icon(Icons.Filled.Image, "Galeri") }

                        // Barkod
                        androidx.compose.material3.SmallFloatingActionButton(
                            onClick = { isCalculateMenuOpen = false },
                            containerColor = Color(0xFFDCFCE7),
                            contentColor = PrimaryGreen,
                            modifier = Modifier.offset(x = (100 * expandProgress).dp, y = (-20 * expandProgress).dp).alpha(expandProgress)
                        ) { Icon(Icons.Filled.QrCodeScanner, "Barkod") }
                    }
                }
            }
        }
    }
}'''

content = re.sub(navhost_end_search, navhost_end_replace, content)

# 3. Remove CalculateScreen function completely
# Finding where CalculateScreen starts and StatisticScreen starts
start_idx = content.find('// --- 2. CALCULATE SCREEN ---')
end_idx = content.find('// --- 3. NE YESEM (RECIPE) SCREEN ---')

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + content[end_idx:]

with open('CalorieCalculator/app/src/main/java/com/example/caloriecalculator/MainActivity.kt', 'w', encoding='utf-8') as f:
    f.write(content)

print("Modification done.")
