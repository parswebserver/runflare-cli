def run():
    print('\nRunflare is a PaaS that allows you to deploy your applications to the cloud with ease.')
    print('To install new version of runflare, run the following command:\n')
    print('For Linux and MacOS:')
    print('\t/bin/bash -c "$(curl -fsSL https://get.runflare.com/install.sh)"\n')
    print('For Windows:')
    print('\tpowershell -Command Invoke-WebRequest -Uri https://get.runflare.com/install.bat -OutFile install.bat; ./install.bat\n')
    print('For more information, visit https://runflare.com\n')

if __name__ == '__main__':
    run()