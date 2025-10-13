# Render R Markdown report to PDF
library(rmarkdown)

# Render the document (working directory is already set by shell)
render("Cont-OFI-HarshH-Report.Rmd")

cat("\nPDF generation complete!\n")
